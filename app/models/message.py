from datetime import datetime
from extensions.database import db
    
class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    chat_id = db.Column(db.Integer, db.ForeignKey("chat.id"), nullable=False)
    sender = db.Column(db.String(10))  # "user" ou "ai"
    content = db.Column(db.Text)
    status = db.Column(db.String(10), default="pending")  # "pending" ou "done"
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

