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

# schedule.every().monday.tuesday.wednesday.thursday.friday.saturday \
#         .at("11:02").at("11:03").at("11:04").do(job)

# schedule.every().saturday.at("11:06").at("11:07").at("11:08").do(job)

# schedule.every().saturday.at("11:08").do(job)
# schedule.every().saturday.at("11:09").do(job)

times = ["11:13", "11:15", "11:16"]
for x in times:
    schedule.every().saturday.at(x).do(job)

schedule.every().weeks.start_day()

# schedule.every(30).to(50).minutes.do(job)
# schedule.every(5).to(10).seconds.do(job)

LOGGER.info("starting \n\n")

while 1:
    schedule.run_pending()
    time.sleep(1)