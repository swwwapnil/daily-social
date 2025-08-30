from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from zoneinfo import ZoneInfo
from .config import SETTINGS
from .run_once import run_once

def main():
    sched = BlockingScheduler(timezone=ZoneInfo(SETTINGS.tz_schedule))
    # 08:00 SGT daily
    trigger = CronTrigger(hour=8, minute=0, second=0, timezone=ZoneInfo(SETTINGS.tz_schedule))
    sched.add_job(run_once, trigger, id="daily_run", replace_existing=True)
    print("Scheduler started. Will run daily at 08:00", SETTINGS.tz_schedule)
    try:
        sched.start()
    except (KeyboardInterrupt, SystemExit):
        print("Scheduler stopped.")

if __name__ == "__main__":
    main()
