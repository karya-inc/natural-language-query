from celery import Celery

app = Celery(
    "database_ops", broker="redis://", backend="redis://", include=["queues.tasks"]
)

if __name__ == "__main__":
    app.start()
