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


schedule.every(.9).seconds.do(job)
schedule.every().minute.do(job_min)
schedule.every().day.at("10:30").do(job)

LOGGER.info("starting \n\n")

while 1:
    schedule.run_pending()
    time.sleep(1)