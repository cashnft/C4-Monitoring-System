from flask import Blueprint, request, jsonify
from .models import Trace, SessionLocal
import logging
from datetime import datetime

tracing_blueprint = Blueprint('tracing', __name__)

#Posrt new trace entry
@tracing_blueprint.route("/", methods=["POST"])
def create_trace():
    # Extract data from request
    data = request.get_json()
    trace_id = data.get("trace_id")
    service = data.get("service")
    operation = data.get("operation")
    duration = data.get("duration")
    timestamp_str = data.get("timestamp")


    if not trace_id or not service or not operation or not duration or not timestamp_str:
        return jsonify({"error": "All fields (trace_id, service, operation, duration, timestamp) are required"}), 400

    try:
       
        timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return jsonify({"error": "Invalid timestamp format. Use 'YYYY-MM-DD HH:MM:SS'"}), 400
    
    # Create a new trace instance
    new_trace = Trace(trace_id=trace_id, service=service, operation=operation, duration=duration, timestamp=timestamp)
    
    # Store the trace in the database
    db = SessionLocal()
    db.add(new_trace)
    db.commit()
    db.refresh(new_trace)
    

    logging.info(f"Created trace for service '{service}' in operation '{operation}' with trace ID '{trace_id}'")
    
    
    return jsonify({
        "message": "Trace entry created",
        "trace": {
            "id": new_trace.id,
            "trace_id": new_trace.trace_id,
            "service": new_trace.service,
            "operation": new_trace.operation,
            "duration": new_trace.duration,
            "timestamp": new_trace.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        }
    }), 201

@tracing_blueprint.route("/<trace_id>", methods=["GET"])
def get_trace(trace_id):
    db = SessionLocal()


    traces = db.query(Trace).filter(Trace.trace_id == trace_id).all()

    if not traces:
        return jsonify({"error": f"No traces found for trace ID '{trace_id}'"}), 404

   
    logging.info(f"Retrieved traces for trace ID '{trace_id}'")
    
    # Format the result
    return jsonify([{
        "service": trace.service,
        "operation": trace.operation,
        "duration": trace.duration,
        "timestamp": trace.timestamp.strftime("%Y-%m-%d %H:%M:%S")
    } for trace in traces])
