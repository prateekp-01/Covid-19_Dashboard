import schedule
import time

def job():
    from subprocess import call
    call(["python", "dashb.py"])

job
schedule.every().day.at("01:00").do(job)

while True:
    schedule.run_pending()
    time.sleep(1)

