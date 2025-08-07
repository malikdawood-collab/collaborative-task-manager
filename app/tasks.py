from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime
from sqlalchemy import or_
from .database import db
from .models import Task, User, Tag

# Create a blueprint for task-related routes
tasks_bp = Blueprint('tasks', __name__)

# --- Helper Functions for Data Serialization ---

def task_to_dict(task):
    """Converts a Task object to a dictionary for JSON serialization."""
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

def user_to_dict(user):
    """Converts a User object to a dictionary for JSON serialization."""
    return {
        'id': user.id,
        'username': user.username,
        'email': user.email
    }

def tag_to_dict(tag):
    """Converts a Tag object to a dictionary for JSON serialization."""
    return {
        'id': tag.id,
        'name': tag.name
    }

# --- Task Endpoints ---

@tasks_bp.route('/tasks', methods=['POST'])
@login_required
def create_task():
    """
    Creates a new task.
    Requires a 'title' in the request JSON.
    """
    data = request.get_json()
    if not data or not data.get('title'):
        return jsonify({'message': 'Title is required to create a task.'}), 400

    title = data.get('title')
    description = data.get('description')
    status = data.get('status', 'pending')
    priority = data.get('priority', 'medium')
    assignee_id = data.get('assignee_id')
    tag_names = data.get('tags', [])

    due_date_str = data.get('due_date')
    due_date = None
    if due_date_str:
        try:
            # Handle both 'Z' and non-'Z' ISO formats
            due_date = datetime.fromisoformat(due_date_str.replace('Z', '+00:00'))
        except ValueError:
            return jsonify({'message': 'Invalid due_date format. Use ISO format (e.g., YYYY-MM-DDTHH:MM:SS.sssZ).'}), 400

    if assignee_id:
        assignee = User.query.get(assignee_id)
        if not assignee:
            return jsonify({'message': 'Invalid assignee ID provided.'}), 400
    else:
        assignee_id = None

    new_task = Task(
        title=title,
        description=description,
        due_date=due_date,
        status=status,
        priority=priority,
        creator_id=current_user.id,
        assignee_id=assignee_id
    )
    
    # Associate tags with the new task
    for tag_name in tag_names:
        tag = Tag.query.filter_by(name=tag_name).first()
        if not tag:
            tag = Tag(name=tag_name)
            db.session.add(tag)
        new_task.tags.append(tag)

    db.session.add(new_task)
    db.session.commit()
    db.session.refresh(new_task)
    return jsonify({'message': 'Task created successfully!', 'task': task_to_dict(new_task)}), 201

@tasks_bp.route('/tasks', methods=['GET'])
@login_required
def get_tasks():
    """
    Retrieves all tasks created by or assigned to the current user.
    """
    tasks = Task.query.filter(
        or_(Task.creator_id == current_user.id, Task.assignee_id == current_user.id)
    ).all()
    return jsonify([task_to_dict(task) for task in tasks]), 200

@tasks_bp.route('/tasks/<int:task_id>', methods=['GET'])
@login_required
def get_task(task_id):
    """
    Retrieves a single task by its ID, if the user has permission to view it.
    """
    task = Task.query.filter(
        (Task.id == task_id) &
        (or_(Task.creator_id == current_user.id, Task.assignee_id == current_user.id))
    ).first()

    if not task:
        return jsonify({'message': 'Task not found or you do not have permission to view it.'}), 404
    return jsonify(task_to_dict(task)), 200

@tasks_bp.route('/tasks/<int:task_id>', methods=['PUT'])
@login_required
def update_task(task_id):
    """
    Updates an existing task by its ID, if the user has permission.
    Permissions: creator or assignee.
    """
    task = Task.query.filter(
        (Task.id == task_id) &
        (or_(Task.creator_id == current_user.id, Task.assignee_id == current_user.id))
    ).first()

    if not task:
        return jsonify({'message': 'Task not found or you do not have permission to update it.'}), 404

    data = request.get_json()
    if not data:
        return jsonify({'message': 'No data provided for update.'}), 400

    # Update fields if they are present in the request data
    if 'title' in data:
        task.title = data['title']
    if 'description' in data:
        task.description = data['description']
    if 'status' in data:
        task.status = data['status']
    if 'priority' in data:
        task.priority = data['priority']
    
    if 'due_date' in data:
        due_date_str = data['due_date']
        if due_date_str is not None:
            try:
                task.due_date = datetime.fromisoformat(due_date_str.replace('Z', '+00:00'))
            except ValueError:
                return jsonify({'message': 'Invalid due_date format. Use ISO format (e.g., YYYY-MM-DDTHH:MM:SS.sssZ).'}), 400
        else:
            task.due_date = None

    if 'assignee_id' in data:
        assignee_id = data['assignee_id']
        if assignee_id is not None:
            assignee = User.query.get(assignee_id)
            if not assignee:
                return jsonify({'message': 'Invalid assignee ID provided.'}), 400
            task.assignee_id = assignee_id
        else:
            task.assignee_id = None
    
    if 'tags' in data:
        new_tag_names = set(data['tags'])
        current_tag_names = {tag.name for tag in task.tags}

        # Remove tags that are no longer in the list
        tags_to_remove = [tag for tag in task.tags if tag.name not in new_tag_names]
        for tag in tags_to_remove:
            task.tags.remove(tag)

        # Add new tags that were not previously associated
        for tag_name in new_tag_names:
            if tag_name not in current_tag_names:
                tag = Tag.query.filter_by(name=tag_name).first()
                if not tag:
                    tag = Tag(name=tag_name)
                    db.session.add(tag)
                task.tags.append(tag)

    db.session.commit()
    db.session.refresh(task)
    return jsonify({'message': 'Task updated successfully!', 'task': task_to_dict(task)}), 200

@tasks_bp.route('/tasks/<int:task_id>', methods=['DELETE'])
@login_required
def delete_task(task_id):
    """
    Deletes a task by its ID, if the current user is the creator.
    NOTE: Deletion is restricted to the creator for security.
    """
    # Find the task, but only if the current user is the creator
    task = Task.query.filter(
        (Task.id == task_id) &
        (Task.creator_id == current_user.id)
    ).first()

    if not task:
        return jsonify({'message': 'Task not found or you do not have permission to delete it.'}), 404
    
    db.session.delete(task)
    db.session.commit()
    return jsonify({'message': 'Task deleted successfully!'}), 200

# --- User & Tag Endpoints ---

@tasks_bp.route('/users', methods=['GET'])
@login_required
def get_all_users():
    """Retrieves a list of all users."""
    users = User.query.all()
    return jsonify([user_to_dict(user) for user in users]), 200

@tasks_bp.route('/users/<int:user_id>/profile', methods=['GET'])
@login_required
def get_user_profile(user_id):
    """
    Retrieves the profile of a specific user, including tasks
    they have created and tasks assigned to them.
    """
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found.'}), 404

    # Fetch tasks created by and assigned to this user
    created_tasks = Task.query.filter_by(creator_id=user_id).all()
    assigned_tasks = Task.query.filter_by(assignee_id=user_id).all()

    return jsonify({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'created_tasks': [task_to_dict(task) for task in created_tasks],
        'assigned_tasks': [task_to_dict(task) for task in assigned_tasks]
    }), 200

@tasks_bp.route('/tags', methods=['GET'])
@login_required
def get_all_tags():
    """Retrieves a list of all available tags."""
    tags = Tag.query.all()
    return jsonify([tag_to_dict(tag) for tag in tags]), 200
