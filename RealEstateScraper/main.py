import os
import sys
import yaml
from pathlib import Path
from PyQt5 import QtWidgets, uic
from datetime import datetime

from site_discovery import discover_sites
from site_scrapers import load_plugin
from utils import db, export
from utils import auth
from utils import vpn
from scheduler.scheduler import ScrapeScheduler

CONFIG_PATH = Path(__file__).resolve().parent / 'config.yaml'

# Allow running in headless environments
if sys.platform.startswith('linux') and not os.environ.get('DISPLAY'):
    os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, master_password: str | None = None):
        super().__init__()
        self.master_password = master_password
        self.session_factory = db.init_db()
        self.job_scheduler = ScrapeScheduler()
        self.load_ui()

    def load_ui(self):
        base = Path(__file__).resolve().parent
        self.scraper = uic.loadUi(base / 'gui' / 'scraper.ui')
        self.discovery = uic.loadUi(base / 'gui' / 'discovery.ui')
        self.scheduler = uic.loadUi(base / 'gui' / 'scheduler.ui')

        tabs = QtWidgets.QTabWidget()
        tabs.addTab(self.discovery, 'اكتشاف')
        tabs.addTab(self.scraper, 'تجريف')
        tabs.addTab(self.scheduler, 'جدولة')
        self.setCentralWidget(tabs)

        self.discovery.refreshButton.clicked.connect(self.refresh_sites)
        self.scraper.startButton.clicked.connect(self.start_scrape)
        self.scheduler.addButton.clicked.connect(self.add_job)
        self.scheduler.removeButton.clicked.connect(self.remove_job)
        self.scheduler.startButton.clicked.connect(self.start_scheduler)
        self.scheduler.stopButton.clicked.connect(self.stop_scheduler)
        self.scheduler.jobsTable.setColumnCount(2)
        self.job_counter = 0

    def refresh_sites(self):
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            cfg = yaml.safe_load(f)
        proxy = cfg.get('network', {}).get('proxy')
        sites = discover_sites(proxy=proxy)
        self.discovery.sitesTable.setRowCount(len(sites))
        self.discovery.sitesTable.setColumnCount(2)
        for i, (name, url) in enumerate(sites):
            self.discovery.sitesTable.setItem(i, 0, QtWidgets.QTableWidgetItem(name))
            self.discovery.sitesTable.setItem(i, 1, QtWidgets.QTableWidgetItem(url))

    def collect_fields(self):
        fields = []
        if self.scraper.titleCheck.isChecked():
            fields.append('title')
        if self.scraper.priceCheck.isChecked():
            fields.append('price')
        if self.scraper.descCheck.isChecked():
            fields.append('description')
        if self.scraper.locCheck.isChecked():
            fields.append('location')
        if self.scraper.imgCheck.isChecked():
            fields.append('images')
        if self.scraper.phoneCheck.isChecked():
            fields.append('phone')
        return fields

    def start_scrape(self):
        fields = self.collect_fields()
        save_dir = self.scraper.pathEdit.text() or 'images'
        export_dir = self.scraper.exportEdit.text() or 'data'
        self.scrape_all(fields, save_dir, export_dir)

    def add_job(self):
        cron = self.scheduler.cronEdit.text() or '0 0 * * *'
        job_id = f'job{self.job_counter}'
        self.job_scheduler.add_job(lambda: self.scrape_all(self.collect_fields(),
                                                          self.scraper.pathEdit.text() or 'images',
                                                          self.scraper.exportEdit.text() or 'data'),
                                   cron, job_id)
        row = self.scheduler.jobsTable.rowCount()
        self.scheduler.jobsTable.insertRow(row)
        self.scheduler.jobsTable.setItem(row, 0, QtWidgets.QTableWidgetItem(job_id))
        self.scheduler.jobsTable.setItem(row, 1, QtWidgets.QTableWidgetItem(cron))
        self.job_counter += 1

    def remove_job(self):
        row = self.scheduler.jobsTable.currentRow()
        if row >= 0:
            job_id = self.scheduler.jobsTable.item(row, 0).text()
            self.job_scheduler.remove_job(job_id)
            self.scheduler.jobsTable.removeRow(row)

    def start_scheduler(self):
        self.job_scheduler.start()

    def stop_scheduler(self):
        self.job_scheduler.shutdown()

    def scrape_all(self, fields, save_dir, export_dir):
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            cfg = yaml.safe_load(f)
        base = Path(cfg['storage'].get('base_path', ''))
        save_dir = base / Path(save_dir)
        export_dir = base / Path(export_dir)
        session = self.session_factory()
        all_listings = []
        self.scraper.progressBar.setValue(0)
        self.scraper.progressBar.setMaximum(len(cfg.get('sites', [])))
        proxy = cfg.get('network', {}).get('proxy')
        vpn_proc = vpn.connect()
        for site in cfg.get('sites', []):
            plugin = load_plugin(site['name'])
            listings = []
            try:
                listings = plugin.scrape(fields, save_dir, self.master_password, proxy)
            except Exception:
                pass
            for item in listings:
                s_obj = session.query(db.Site).filter_by(name=site['name']).first()
                if not s_obj:
                    s_obj = db.Site(name=site['name'], url=site['url'])
                    session.add(s_obj)
                    session.commit()
                listing = db.Listing(
                    site_id=s_obj.id,
                    title=item.get('title'),
                    price=item.get('price'),
                    description=item.get('description'),
                    location=item.get('location'),
                    phone=item.get('phone')
                )
                session.add(listing)
                session.commit()
                for img_path in item.get('images', []):
                    session.add(db.Image(listing_id=listing.id, path=img_path))
                session.commit()
            all_listings.extend(listings)
            self.scraper.progressBar.setValue(self.scraper.progressBar.value() + 1)
        session.close()
        export_dir.mkdir(parents=True, exist_ok=True)
        if 'csv' in cfg['export']['formats']:
            export.export_csv(all_listings, export_dir / 'export.csv')
        if 'json' in cfg['export']['formats']:
            export.export_json(all_listings, export_dir / 'export.json')
        vpn.disconnect(vpn_proc)
        if cfg.get('notifications', {}).get('toast'):
            from utils.notify import notify
            notify('انتهى التجريف', f'تم حفظ {len(all_listings)} إعلاناً')


def login_dialog():
    base = Path(__file__).resolve().parent
    dlg = uic.loadUi(base / 'gui' / 'login.ui')
    dlg.buttonBox.accepted.connect(dlg.accept)
    dlg.buttonBox.rejected.connect(dlg.reject)
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        cfg = yaml.safe_load(f)
    for site in cfg.get('sites', []):
        dlg.siteCombo.addItem(site['name'])
    if dlg.exec_() == QtWidgets.QDialog.Accepted:
        user = dlg.userEdit.text()
        pwd = dlg.passEdit.text()
        master = dlg.masterEdit.text() or pwd
        site = dlg.siteCombo.currentText()
        auth.save_credentials(site, user, pwd, master)
        return master
    return None


def main():
    app = QtWidgets.QApplication(sys.argv)
    master_password = login_dialog()
    win = MainWindow(master_password)
    win.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
