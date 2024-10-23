from flask import Flask
from api.metrics import metrics_blueprint
from api.logging import logging_blueprint
from api.tracing import tracing_blueprint
from api.models import init_db

app = Flask(__name__)

#initialize the database
init_db()

#register the blueprints
app.register_blueprint(metrics_blueprint, url_prefix="/metrics")
app.register_blueprint(logging_blueprint, url_prefix="/logs")
app.register_blueprint(tracing_blueprint, url_prefix="/traces")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
