import os
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from .orchestrator import Orchestrator

logger = logging.getLogger(__name__)


class SchedulerService:
    """Simple scheduler wrapper.

    Modes:
    - local: runs at an interval defined by INTERVAL_MINUTES (default 60)
    - once: runs a single pipeline pass and exits

    Note: For Vercel deployment, their free plan allows cron jobs once per day.
    Use the provided GitHub Actions workflow for daily scheduled runs that commit
    generated `public/` content back to the repository (see .github/workflows).
    """

    def __init__(self, orchestrator=None):
        self.orch = orchestrator or Orchestrator()
        self.scheduler = BackgroundScheduler()

    def run_once(self):
        logger.info("Running pipeline once at %s", datetime.utcnow().isoformat())
        try:
            path = self.orch.run_once()
            logger.info("Publish result: %s", path)
        except Exception as e:
            logger.exception("Pipeline run failed: %s", e)

    def run_local(self, interval_minutes=60):
        interval_minutes = int(os.getenv('INTERVAL_MINUTES', interval_minutes))
        logger.info("Starting local scheduler: interval %s minutes", interval_minutes)
        self.scheduler.add_job(self.run_once, 'interval', minutes=interval_minutes, next_run_time=datetime.utcnow())
        self.scheduler.start()
        try:
            # Keep the process alive
            import time
            while True:
                time.sleep(10)
        except (KeyboardInterrupt, SystemExit):
            logger.info("Shutting down scheduler")
            self.scheduler.shutdown()
