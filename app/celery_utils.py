from celery import Celery
from config import REDIS_BACKEND, REDIS_BROKER
from flask import Flask


def celery_app_instance(app: Flask) -> Celery:
    celery = Celery(
        app.import_name,
        backend=REDIS_BACKEND,
        broker=REDIS_BROKER
    )
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask

    return celery
