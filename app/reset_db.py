# import sys
# from pathlib import Path

# # Add the root project directory to the Python path
# sys.path.append(str(Path(__file__).resolve().parent.parent))

# from app import create_app, db

# app = create_app()

# with app.app_context():
#     db.drop_all()  # Drop all tables
#     db.create_all()  # Recreate all tables
#     print("Database has been reset.")
