from time import sleep
from threading import Thread, Lock
import logging as log


class ProtectedResource:
    """
    ProtectedResource is an example resource that requires synchronization to
    update (set).
    """
    def __init__(self):
        self._val = -1

    @property
    def val(self):
        return self._val

    @val.setter
    def val(self, val):
        self._val = val


def threaded_job(job_id, delay_sec, lock, lock_timeout, resource):
    def job(job_id, delay_sec, lock_timeout, resource):
        lock_acquired = lock.acquire(timeout=lock_timeout)
        if not lock_acquired:
            log.warning(f"[{job_id}] lock not acquired")
            return
        try:
            log.info(f"[{job_id}] lock acquired")
            log.info(f"[{job_id}] before set, resource: {resource.val}")
            resource.val = job_id
            log.info(f"[{job_id}] after set, resource: {resource.val}")
            log.info(f"[{job_id}] sleeping for {delay_sec}s")
            sleep(delay_sec)
        finally:
            log.info(f"[{job_id}] releasing lock")
            log.info(f"[{job_id}] resource: {resource.val}")
            lock.release()

    job_thread = Thread(
        target=job,
        kwargs={
            "job_id": job_id,
            "delay_sec": delay_sec,
            "lock_timeout": lock_timeout,
            "resource": resource,
        },
    )
    job_thread.start()
 

if __name__ == '__main__':
    log_format = "%(asctime)s [%(levelname)s] line %(lineno)d): %(message)s"
    log_level = log.INFO
    log.basicConfig(level=log_level, format=log_format)
    log.info("Python threads example")
    resource_lock = Lock()
    resource = ProtectedResource()

    log.info("")
    log.info("Overlapping case:")
    lock_timeout = 2
    delay_sec = 1.5 
    threaded_job("job_1", delay_sec, resource_lock, lock_timeout, resource)
    threaded_job("job_2", delay_sec, resource_lock, lock_timeout, resource)

    sleep(5)
    log.info("")
    log.info("Lock acquire failure case:")
    lock_timeout = 2
    delay_sec = 3
    threaded_job("job_1", delay_sec, resource_lock, lock_timeout, resource)
    threaded_job("job_2", delay_sec, resource_lock, lock_timeout, resource)


