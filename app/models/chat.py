from datetime import datetime

from extensions.database import db
    
class Chat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    title = db.Column(db.Text)
    model = db.Column(db.String(30))
    agent = db.Column(db.String(30))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
