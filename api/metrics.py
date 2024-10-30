from aioflask import Blueprint, request, jsonify
from sqlalchemy import select
import logging
from datetime import datetime
from .models import Metric, get_db

metrics_blueprint = Blueprint('metrics', __name__)

#create a new metric post
@metrics_blueprint.route("/", methods=["POST"])
async def create_metric():
    # Extracting data from the request
    data = request.get_json()
    service = data.get("service")
    metric_type = data.get("metric_type")
    value = data.get("value")
    timestamp_str = data.get("timestamp")
    
    #validate required fields
    if not service or not metric_type or not value or not timestamp_str:
        return jsonify({
            "error": "All fields (service, metric_type, value, timestamp) are required"
        }), 400

    try:
        timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return jsonify({
            "error": "Invalid timestamp format. Use 'YYYY-MM-DD HH:MM:SS'"
        }), 400
    
    # Create a new metric instance
    new_metric = Metric(
        service=service,
        metric_type=metric_type,
        value=value,
        timestamp=timestamp
    )
    
    #store the metric in the database using async session
    async for session in get_db():
        try:
            session.add(new_metric)
            await session.commit()
            await session.refresh(new_metric)
            
            logging.info(
                f"Created metric for service '{service}': "
                f"{metric_type} - {value} at {timestamp}"
            )
            
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
        except Exception as e:
            await session.rollback()
            logging.error(f"Error creating metric: {str(e)}")
            return jsonify({"error": "Failed to create metric"}), 500

#GET metrics by service
@metrics_blueprint.route("/<service>", methods=["GET"])
async def get_metrics(service):
    async for session in get_db():
        try:
            # Use select statement with async execution
            result = await session.execute(
                select(Metric).filter(Metric.service == service)
            )
            metrics = result.scalars().all()
            
            if not metrics:
                return jsonify({
                    "error": f"No metrics found for service '{service}'"
                }), 404
                
            logging.info(f"Retrieved metrics for service '{service}'")
            
            return jsonify([{
                "metric_type": metric.metric_type,
                "value": metric.value,
                "timestamp": metric.timestamp.strftime("%Y-%m-%d %H:%M:%S")
            } for metric in metrics])
            
        except Exception as e:
            logging.error(f"Error retrieving metrics: {str(e)}")
            return jsonify({"error": "Failed to retrieve metrics"}), 500