from datetime import datetime
from extensions.database import db
    
class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    chat_id = db.Column(db.Integer, db.ForeignKey("chat.id"), nullable=False)
    sender = db.Column(db.String(10))
    content = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

