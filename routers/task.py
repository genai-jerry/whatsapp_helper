from flask import Blueprint, render_template, request, jsonify, abort
from flask_login import login_required, current_user
from store.tasks_store import *

task_blueprint = Blueprint('task', __name__)

@task_blueprint.route('/')
@login_required
def get_tasks_api():
    opportunity_id = request.args.get("opportunity_id")
    employee_id = request.args.get("employee_id")
    tasks_type = request.args.get("tasks_type", "due")
    
    if opportunity_id:
        tasks, _ = get_all_tasks_for_opportunity(opportunity_id, employee_id)
    else:
        tasks, _ = get_tasks_due(employee_id); # get_tasks()
    print(f"tasks: {tasks}")
    return jsonify({"tasks": tasks}), 200

@task_blueprint.route('<string:task_id>')
@login_required
def get_task_api(task_id):
    task = None # get_task(task_id)
    if not task:
        abort(404, description="Task not found")
    return render_template('task_detail.html', task=task)

@task_blueprint.route('create', methods=['GET'])
@login_required
def get_create_task_modal_api():
    return render_template('task/create_modal.html')

@task_blueprint.route('/', methods=['POST'])
@login_required
def create_task_api():
    selected_employee_id = request.form.get("selected_employee_id")
    if selected_employee_id == "0":
        employee_id = None
    else:
        employee_id = selected_employee_id
    task_data = {
        "opportunity_id": request.form.get("opportunity_id"),
        "due_date": request.form.get("due_date"),
        "task_details": request.form.get("description"),
        "status": "pending",
        "user_id": employee_id if employee_id else current_user.id  # Add the current user's ID
    }
    
    new_task = create_task(task_data["user_id"], '', task_data["task_details"], 
                           task_data["due_date"], task_data["opportunity_id"], current_user.id)
    return jsonify({"message": "Task created successfully", "task_id": new_task["id"]}), 201

@task_blueprint.route('<string:task_id>/status', methods=['PUT'])
@login_required
def update_task_status_api(task_id):
    status = request.json.get("status")
    updated_task = update_task_status(task_id, status)
    if not updated_task:
        abort(404, description="Task not found")
    return jsonify({"message": "Task updated successfully", "task": updated_task})

@task_blueprint.route('<string:task_id>', methods=['PUT'])
@login_required
def update_task_api(task_id):
    task_data = {
        "title": request.form.get("title"),
        "description": request.form.get("description"),
        "due_date": request.form.get("due_date"),
        "status": request.form.get("status"),
    }
    updated_task = update_task(task_id, task_data)
    if not updated_task:
        abort(404, description="Task not found")
    return jsonify({"message": "Task updated successfully", "task": updated_task})

@task_blueprint.route('<string:task_id>', methods=['DELETE'])
@login_required
def delete_task_api(task_id):
    deleted = delete_task(task_id)
    if not deleted:
        abort(404, description="Task not found")
    return jsonify({"message": "Task deleted successfully"})

