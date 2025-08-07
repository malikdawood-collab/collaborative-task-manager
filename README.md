# Collaborative Task Manager

A full-stack task and project management web app built with **Flask** (Python) for the backend and **React** for the frontend. It supports user authentication, real-time project collaboration, task assignment, due-date sorting, Kanban-style boards, and more.

---

## 🚀 Features

- **User Accounts & Authentication**  
  - Secure registration / login with hashed passwords  
  - Session management via Flask-Login & HTTP-only cookies  
- **Project Management**  
  - Create new projects (auto-generate a unique join code)  
  - Join existing projects by code  
  - View project members  
  - Mark projects as completed and archive them  
- **Task Management**  
  - CRUD operations for tasks within a project  
  - Assign tasks to team members  
  - Add due dates, priorities, and tags  
  - Filter tasks by “created by me” / “assigned to me” / all  
  - Sort tasks by due date (ascending or descending)  
  - (Future) Kanban drag-and-drop board  
- **Tech Stack**  
  - **Backend:** Flask, SQLAlchemy, Flask-Login, SQLite  
  - **Frontend:** React (Create React App), Tailwind CSS  
  - **API:** RESTful routes under `/auth`, `/api/projects`, `/api/tasks`  
  - **CORS & Cookies:** React ↔ Flask via `fetch(..., { credentials: 'include' })`  

---

## 📦 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/malikdawood-collab/collaborative-task-manager.git
cd collaborative-task-manager

.
├── app/                   # Flask backend
│   ├── __init__.py        # create_app, CORS, blueprints
│   ├── auth.py            # login, register, status, logout
│   ├── projects.py        # project CRUD, members, complete/archive
│   ├── tasks.py           # task CRUD, tag handling
│   ├── models.py          # SQLAlchemy models
│   ├── database.py        # SQLAlchemy instance
│   └── migrations/        # ad-hoc SQL migration scripts
├── requirements.txt       # Python dependencies
├── migratescript.py       # example migration runner
├── collaborative-task-manager-frontend/
│   ├── public/
│   └── src/               # React application
│       └── App.js         # main logic, fetch calls, UI
├── README.md              # <-- You’re here
└── .gitignore
# Collaborative Task Manager

Live Demo: 🔗 https://malikdawood-collab.github.io/collaborative-task-manager-frontend/

A full-stack task & project management app built with Flask + React…
