# migrate_add_project_id.py
from sqlalchemy import text
from app import create_app, db

def main():
    app = create_app()
    with app.app_context():
        # Inspect existing columns
        result = db.session.execute(text("PRAGMA table_info(task);")).fetchall()
        cols = [row[1] for row in result]

        if "project_id" in cols:
            print("⚠️  project_id already present, nothing to do.")
        else:
            # Add the new column
            db.session.execute(text("ALTER TABLE task ADD COLUMN project_id INTEGER;"))
            db.session.commit()
            print("✅ project_id column added.")

if __name__ == "__main__":
    main()
