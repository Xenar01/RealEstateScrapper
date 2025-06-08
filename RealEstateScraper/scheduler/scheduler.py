from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger


class ScrapeScheduler:
    def __init__(self):
        self.scheduler = BackgroundScheduler()

    def add_job(self, func, cron_expr, job_id):
        trigger = CronTrigger.from_crontab(cron_expr)
        self.scheduler.add_job(func, trigger, id=job_id, replace_existing=True)

    def remove_job(self, job_id):
        self.scheduler.remove_job(job_id)

    def start(self):
        if not self.scheduler.running:
            self.scheduler.start()

    def shutdown(self):
        if self.scheduler.running:
            self.scheduler.shutdown()
