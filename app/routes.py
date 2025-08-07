from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from .models import Task, Tag
from .database import db
from sqlalchemy import or_

main_bp = Blueprint('main_bp', __name__)

# Helper function to serialize tasks
def task_to_dict(task):
    """Converts a task object to a dictionary."""
    return {
        'id': task.id,
        'title': task.title,
        'description': task.description,
        'due_date': task.due_date.isoformat() if task.due_date else None,
        'status': task.status,
        'priority': task.priority,
        'creator_id': task.creator_id,
        'creator_username': task.creator.username,
        'assignee_id': task.assignee_id,
        'assignee_username': task.assignee.username if task.assignee else None,
        'tags': [tag.name for tag in task.tags]
    }

@main_bp.route('/tasks', methods=['GET'])
@login_required
def get_tasks():
    # Corrected: Get all tasks created by the user or assigned to the user
    # Use or_ to combine the query results
    tasks = Task.query.filter(or_(
        Task.creator_id == current_user.id,
        Task.assignee_id == current_user.id
    )).all()
    task_list = [task_to_dict(t) for t in tasks]
    return jsonify(task_list), 200

@main_bp.route('/tasks', methods=['POST'])
@login_required
def add_task():
    data = request.get_json()
    new_task = Task(
        title=data.get('title'),
        description=data.get('description'),
        # Corrected: Use 'creator_id' instead of 'user_id'
        creator_id=current_user.id
    )
    db.session.add(new_task)
    db.session.commit()
    return jsonify({'id': new_task.id, 'title': new_task.title}), 201

@main_bp.route('/tasks/<int:task_id>', methods=['PUT'])
@login_required
def update_task(task_id):
    task = Task.query.get_or_404(task_id)
    # Check if the current user is the creator or assignee
    if task.creator_id != current_user.id and task.assignee_id != current_user.id:
        return jsonify({'message': 'Unauthorized'}), 403

    data = request.get_json()
    task.title = data.get('title', task.title)
    task.description = data.get('description', task.description)
    task.status = data.get('status', task.status)
    db.session.commit()
    return jsonify(task_to_dict(task)), 200

@main_bp.route('/tasks/<int:task_id>', methods=['DELETE'])
@login_required
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    # Only the creator can delete the task
    if task.creator_id != current_user.id:
        return jsonify({'message': 'Unauthorized'}), 403
    
    db.session.delete(task)
    db.session.commit()
    return jsonify({'message': 'Task deleted successfully'}), 200

