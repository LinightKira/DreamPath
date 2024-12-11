from app_server.db import db
from app_server import app

with app.app_context():
    db.create_all()
    print("All tables created")
