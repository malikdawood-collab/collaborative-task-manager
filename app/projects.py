# app/projects.py

from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from .database import db
from .models import Project, Task, Tag, project_members
from datetime import datetime

projects_bp = Blueprint('projects_bp', __name__)

def project_to_dict(p: Project):
    return {
        'id': p.id,
        'title': p.title,
        'join_code': p.join_code,
        'is_completed': p.is_completed,
        'members': [{'id': u.id, 'username': u.username} for u in p.members]
    }

def task_to_dict(t: Task):
    return {
        'id': t.id,
        'title': t.title,
        'description': t.description,
        'due_date': t.due_date.isoformat() if t.due_date else None,
        'status': t.status,
        'priority': t.priority,
        'creator_id': t.creator_id,
        'creator_username': t.creator.username,
        'assignee_id': t.assignee_id,
        'assignee_username': t.assignee.username if t.assignee else None,
        'tags': [tag.name for tag in t.tags]
    }

# ── Active Projects ───────────────────────────────────────────────
@projects_bp.route('', methods=['GET'])
@login_required
def list_projects():
    """List all *active* (not completed) projects the current user belongs to."""
    projs = (
        Project.query
        .join(project_members)
        .filter(project_members.c.user_id == current_user.id)
        .filter(Project.is_completed == False)
        .all()
    )
    return jsonify([project_to_dict(p) for p in projs]), 200

# ── Completed Projects ────────────────────────────────────────────
@projects_bp.route('/completed', methods=['GET'])
@login_required
def list_completed_projects():
    """List all *completed* projects the current user belongs to."""
    projs = (
        Project.query
        .join(project_members)
        .filter(project_members.c.user_id == current_user.id)
        .filter(Project.is_completed == True)
        .all()
    )
    return jsonify([project_to_dict(p) for p in projs]), 200

# ── Create Project ────────────────────────────────────────────────
@projects_bp.route('', methods=['POST'])
@login_required
def create_project():
    data = request.get_json() or {}
    title = data.get('title')
    if not title:
        return jsonify({'message': 'Title is required'}), 400

    p = Project(title=title)
    p.members.append(current_user)
    db.session.add(p)
    db.session.commit()

    return jsonify(project_to_dict(p)), 201

# ── Join Project ─────────────────────────────────────────────────
@projects_bp.route('/join', methods=['POST'])
@login_required
def join_project():
    data = request.get_json() or {}
    code = data.get('join_code')
    if not code:
        return jsonify({'message': 'Join code required'}), 400

    p = Project.query.filter_by(join_code=code).first()
    if not p:
        return jsonify({'message': 'Invalid join code'}), 404

    if current_user in p.members:
        return jsonify({'message': 'Already a member'}), 200

    p.members.append(current_user)
    db.session.commit()
    return jsonify({'message': f'Joined project "{p.title}"'}), 200

# ── Project Members ──────────────────────────────────────────────
@projects_bp.route('/<int:project_id>/members', methods=['GET'])
@login_required
def project_members_list(project_id):
    p = Project.query.get_or_404(project_id)
    if current_user not in p.members:
        return jsonify({'message': 'Forbidden'}), 403

    members = [
        {'id': u.id, 'username': u.username, 'email': u.email}
        for u in p.members
    ]
    return jsonify(members), 200

# ── List Tasks ────────────────────────────────────────────────────
@projects_bp.route('/<int:project_id>/tasks', methods=['GET'])
@login_required
def project_tasks(project_id):
    p = Project.query.get_or_404(project_id)
    if current_user not in p.members:
        return jsonify({'message': 'Forbidden'}), 403

    return jsonify([task_to_dict(t) for t in p.tasks]), 200

# ── Create Task ───────────────────────────────────────────────────
@projects_bp.route('/<int:project_id>/tasks', methods=['POST'])
@login_required
def create_project_task(project_id):
    p = Project.query.get_or_404(project_id)
    if current_user not in p.members:
        return jsonify({'message': 'Forbidden'}), 403

    data = request.get_json() or {}
    title = data.get('title')
    if not title:
        return jsonify({'message': 'Title required'}), 400

    due = data.get('due_date')
    due_date = datetime.fromisoformat(due) if due else None

    t = Task(
        title=title,
        description=data.get('description'),
        status=data.get('status', 'pending'),
        priority=data.get('priority', 'medium'),
        creator_id=current_user.id,
        assignee_id=data.get('assignee_id'),
        project_id=project_id,
        due_date=due_date
    )
    for name in data.get('tags', []):
        tag = Tag.query.filter_by(name=name).first() or Tag(name=name)
        db.session.add(tag)
        t.tags.append(tag)

    db.session.add(t)
    db.session.commit()

    return jsonify({
        'message': 'Task created',
        'task': task_to_dict(t)
    }), 201

# ── Mark Project Completed ────────────────────────────────────────
@projects_bp.route('/<int:project_id>/complete', methods=['PUT'])
@login_required
def complete_project(project_id):
    p = Project.query.get_or_404(project_id)
    if current_user not in p.members:
        return jsonify({'message': 'Forbidden'}), 403

    p.is_completed = True
    db.session.commit()
    return jsonify({'message': 'Project marked completed.'}), 200
