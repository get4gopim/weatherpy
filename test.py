import time
from utility import util
from queue import Queue
import schedule
import os
import logging
import threading
from service import HtmlParser2

job_queue = Queue()


def worker_main():
    while 1:
        try:
            job_func, job_args = job_queue.get()
            job_func(*job_args)
            job_queue.task_done()
        except BaseException as ex:
            LOGGER.error(f'worker_main : {repr(ex)}')


def add_scheduler():
    # Update time every minutes
    schedule.every().minute.at(':00').do(job_queue.put, (every_sec, []))


def every_sec():
    LOGGER.info ('Time partial update')


if __name__ == '__main__':
    logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"), format='%(asctime)s %(message)s')
    logging.getLogger('schedule').propagate = False

    LOGGER = logging.getLogger(__name__)

    worker_thread = threading.Thread(target=worker_main)
    worker_thread.start()

    add_scheduler()

    HtmlParser2.call_weather_api('4ef51d4289943c7792cbe77dee741bff9216f591eed796d7a5d598c38828957d')

    while 1:
        schedule.run_pending()
        time.sleep(1)

