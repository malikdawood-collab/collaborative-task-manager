# migrations/add_project_is_completed.py
from app import create_app, db
from sqlalchemy import text

app = create_app()

with app.app_context():
    # Add the new is_completed column (default false)
    db.session.execute(
        text('ALTER TABLE project ADD COLUMN is_completed BOOLEAN NOT NULL DEFAULT 0;')
    )
    db.session.commit()
    print("✅ is_completed column added.")
