from aioflask import Blueprint, request, jsonify
from sqlalchemy import select
import logging
from datetime import datetime
from .models import Log, get_db

logging_blueprint = Blueprint('logging', __name__)

@logging_blueprint.route("/", methods=["POST"])
async def create_log():
    data = request.get_json()
    service = data.get("service")
    level = data.get("level")
    message = data.get("message")
    timestamp_str = data.get("timestamp")

    if not service or not level or not message or not timestamp_str:
        return jsonify({
            "error": "All fields (service, level, message, timestamp) are required"
        }), 400

    try:
        timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return jsonify({
            "error": "Invalid timestamp format. Use 'YYYY-MM-DD HH:MM:SS'"
        }), 400

    new_log = Log(
        service=service,
        level=level,
        message=message,
        timestamp=timestamp
    )

    async for session in get_db():
        try:
            session.add(new_log)
            await session.commit()
            await session.refresh(new_log)

            logging.info(
                f"Created log for service '{service}': {level} - {message}"
            )

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
        except Exception as e:
            await session.rollback()
            logging.error(f"Error creating log: {str(e)}")
            return jsonify({"error": "Failed to create log entry"}), 500

@logging_blueprint.route("/<service>", methods=["GET"])
async def get_logs(service):
    async for session in get_db():
        try:
            result = await session.execute(
                select(Log).filter(Log.service == service)
            )
            logs = result.scalars().all()

            if not logs:
                return jsonify({
                    "error": f"No logs found for service '{service}'"
                }), 404

            logging.info(f"Retrieved logs for service '{service}'")

            return jsonify([{
                "level": log.level,
                "message": log.message,
                "timestamp": log.timestamp.strftime("%Y-%m-%d %H:%M:%S")
            } for log in logs])

        except Exception as e:
            logging.error(f"Error retrieving logs: {str(e)}")
            return jsonify({"error": "Failed to retrieve logs"}), 500