import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from RealEstateScraper.scheduler.scheduler import ScrapeScheduler


def test_scheduler_lifecycle():
    sch = ScrapeScheduler()
    sch.add_job(lambda: None, '* * * * *', 'job1')
    sch.start()
    assert sch.scheduler.running
    sch.shutdown()
    assert not sch.scheduler.running
