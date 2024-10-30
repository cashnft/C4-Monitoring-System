from aioflask import Blueprint, request, jsonify
from sqlalchemy import select
import logging
from datetime import datetime
from .models import Trace, get_db

tracing_blueprint = Blueprint('tracing', __name__)

@tracing_blueprint.route("/", methods=["POST"])
async def create_trace():
    data = request.get_json()
    trace_id = data.get("trace_id")
    service = data.get("service")
    operation = data.get("operation")
    duration = data.get("duration")
    timestamp_str = data.get("timestamp")

    if not trace_id or not service or not operation or not duration or not timestamp_str:
        return jsonify({
            "error": "All fields (trace_id, service, operation, duration, timestamp) are required"
        }), 400

    try:
        timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return jsonify({
            "error": "Invalid timestamp format. Use 'YYYY-MM-DD HH:MM:SS'"
        }), 400

    new_trace = Trace(
        trace_id=trace_id,
        service=service,
        operation=operation,
        duration=duration,
        timestamp=timestamp
    )

    async for session in get_db():
        try:
            session.add(new_trace)
            await session.commit()
            await session.refresh(new_trace)

            logging.info(
                f"Created trace for service '{service}' "
                f"operation '{operation}' with trace ID '{trace_id}'"
            )

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
        except Exception as e:
            await session.rollback()
            logging.error(f"Error creating trace: {str(e)}")
            return jsonify({"error": "Failed to create trace entry"}), 500

@tracing_blueprint.route("/<trace_id>", methods=["GET"])
async def get_trace(trace_id):
    async for session in get_db():
        try:
            result = await session.execute(
                select(Trace).filter(Trace.trace_id == trace_id)
            )
            traces = result.scalars().all()

            if not traces:
                return jsonify({
                    "error": f"No traces found for trace ID '{trace_id}'"
                }), 404

            logging.info(f"Retrieved traces for trace ID '{trace_id}'")

            return jsonify([{
                "service": trace.service,
                "operation": trace.operation,
                "duration": trace.duration,
                "timestamp": trace.timestamp.strftime("%Y-%m-%d %H:%M:%S")
            } for trace in traces])

        except Exception as e:
            logging.error(f"Error retrieving traces: {str(e)}")
            return jsonify({"error": "Failed to retrieve traces"}), 500