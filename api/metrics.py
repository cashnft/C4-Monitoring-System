from flask import Blueprint, request, jsonify
from .models import Metric, SessionLocal
import logging
from datetime import datetime

metrics_blueprint = Blueprint('metrics', __name__)

# cerates a new metric post
@metrics_blueprint.route("/", methods=["POST"])
def create_metric():
    #extracting data from the request
    data = request.get_json()
    service = data.get("service")
    metric_type = data.get("metric_type")
    value = data.get("value")
    timestamp_str = data.get("timestamp")
    
   
    if not service or not metric_type or not value or not timestamp_str:
        return jsonify({"error": "All fields (service, metric_type, value, timestamp) are required"}), 400

    try:
        
        timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return jsonify({"error": "Invalid timestamp format. Use 'YYYY-MM-DD HH:MM:SS'"}), 400
    
    #Create a new metric instance
    new_metric = Metric(service=service, metric_type=metric_type, value=value, timestamp=timestamp)
    
    #storing the metric in the database
    db = SessionLocal()
    db.add(new_metric)
    db.commit()
    db.refresh(new_metric)
    

    logging.info(f"Created metric for service '{service}': {metric_type} - {value} at {timestamp}")
    
  
    return jsonify({
        "message": "Metric created",
        "metric": {
            "id": new_metric.id,
            "service": new_metric.service,
            "metric_type": new_metric.metric_type,
            "value": new_metric.value,
            "timestamp": new_metric.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        }
    }), 201

# GET metrics by service
@metrics_blueprint.route("/<service>", methods=["GET"])
def get_metrics(service):
  
    db = SessionLocal()

    metrics = db.query(Metric).filter(Metric.service == service).all()
    
    if not metrics:
        return jsonify({"error": f"No metrics found for service '{service}'"}), 404
    logging.info(f"Retrieved metrics for service '{service}'")
    
    return jsonify([{
        "metric_type": metric.metric_type,
        "value": metric.value,
        "timestamp": metric.timestamp.strftime("%Y-%m-%d %H:%M:%S")
    } for metric in metrics])
