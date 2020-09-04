import schedule
import time
import logging
import os

logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"), format='%(asctime)s %(message)s')
LOGGER = logging.getLogger(__name__)


def job():
    LOGGER.info ("Doing stuff...\n")


def job_min():
    LOGGER.info ("Min stuff...\n\n")


# schedule.every(.9).seconds.do(job)
# schedule.every().minute.do(job_min)
# schedule.every().minute.at(":21").do(job)

schedule.every().monday.tuesday.wednesday.thursday.friday.saturday \
        .at("06:30").at("07:00").at("07:30").do(job)

# schedule.every(30).to(50).minutes.do(job)
# schedule.every(5).to(10).seconds.do(job)

LOGGER.info("starting \n\n")

while 1:
    schedule.run_pending()
    time.sleep(1)