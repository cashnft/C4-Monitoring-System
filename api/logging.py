from flask import Blueprint, request, jsonify
from .models import Log, SessionLocal
import logging
from datetime import datetime

logging_blueprint = Blueprint('logging', __name__)

# POST new log entry
@logging_blueprint.route("/", methods=["POST"])
def create_log():
  
    data = request.get_json()
    service = data.get("service")
    level = data.get("level")
    message = data.get("message")
    timestamp_str = data.get("timestamp")


    if not service or not level or not message or not timestamp_str:
        return jsonify({"error": "All fields (service, level, message, timestamp) are required"}), 400

    try:
    
        timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return jsonify({"error": "Invalid timestamp format. Use 'YYYY-MM-DD HH:MM:SS'"}), 400
    

    new_log = Log(service=service, level=level, message=message, timestamp=timestamp)
    
    #storing the log in the database
    db = SessionLocal()
    db.add(new_log)
    db.commit()
    db.refresh(new_log)
    
  
    logging.info(f"Created log for service '{service}': {level} - {message} at {timestamp}")
    
    # resp with the created log
    return jsonify({
        "message": "Log entry created",
        "log": {
            "id": new_log.id,
            "service": new_log.service,
            "level": new_log.level,
            "message": new_log.message,
            "timestamp": new_log.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        }
    }), 201

 # get logs by service
@logging_blueprint.route("/<service>", methods=["GET"])
def get_logs(service):
   
    db = SessionLocal()

   
    logs = db.query(Log).filter(Log.service == service).all()

    if not logs:
        return jsonify({"error": f"No logs found for service '{service}'"}), 404

    
    logging.info(f"Retrieved logs for service '{service}'")
    
    # Format the result
    return jsonify([{
        "level": log.level,
        "message": log.message,
        "timestamp": log.timestamp.strftime("%Y-%m-%d %H:%M:%S")
    } for log in logs])
