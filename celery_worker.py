import os
import sys

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from main import celery_app

if __name__ == "__main__":
    celery_app.worker_main(["worker", "--loglevel=info", "--pool=solo"])
