from flask import Flask, request, jsonify
from sqlalchemy.orm import Session
from .models import Task, SessionLocal
import logging

app = Flask(__name__)

#init lgoger
logging.basicConfig(level=logging.INFO)


from prometheus_flask_exporter import PrometheusMetrics
metrics = PrometheusMetrics(app)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

#xreate a new task
@app.route("/tasks", methods=["POST"])
def create_task():
    data = request.get_json()
    description = data.get("description")

    if not description:
        return jsonify({"error": "Description is required"}), 400

    new_task = Task(description=description)
    
    db = SessionLocal()
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    
    logging.info(f"Created task: {new_task.description}")
    return jsonify({"message": "Task created", "task": {"id": new_task.id, "description": new_task.description}}), 201

# retrieve a task by id
@app.route("/tasks/<int:task_id>", methods=["GET"])
def get_task(task_id):
    db = SessionLocal()
    task = db.query(Task).filter(Task.id == task_id).first()
    
    if not task:
        return jsonify({"error": "Task not found"}), 404
    
    return jsonify({"id": task.id, "description": task.description, "status": task.status})

# update a task by id
@app.route("/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    data = request.get_json()
    description = data.get("description")
    status = data.get("status")

    db = SessionLocal()
    task = db.query(Task).filter(Task.id == task_id).first()

    if not task:
        return jsonify({"error": "Task not found"}), 404

    if description:
        task.description = description
    if status:
        task.status = status

    db.commit()
    logging.info(f"Updated task {task.id}: {task.description} - {task.status}")
    return jsonify({"message": "Task updated", "task": {"id": task.id, "description": task.description, "status": task.status}})

#delete a task by ID
@app.route("/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    db = SessionLocal()
    task = db.query(Task).filter(Task.id == task_id).first()

    if not task:
        return jsonify({"error": "Task not found"}), 404

    db.delete(task)
    db.commit()

    logging.info(f"Deleted task {task.id}")
    return jsonify({"message": "Task deleted"})


@app.route("/tasks", methods=["GET"])
def list_tasks():
    db = SessionLocal()
    tasks = db.query(Task).all()

    return jsonify([{"id": task.id, "description": task.description, "status": task.status} for task in tasks])
