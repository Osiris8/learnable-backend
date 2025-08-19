from datetime import datetime
from turtle import title
from extensions import db
    
class Chat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    title = db.Column(db.Text)
    title_ai_summarize = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

