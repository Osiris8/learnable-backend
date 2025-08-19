import os
import asyncio
from flask import Blueprint, request, jsonify, Response
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.ollama import ollama_service
from extensions import db
from app.models.chat import Chat
from app.models.message import Message

chat_bp = Blueprint("chats", __name__)

@chat_bp.route("/chat", methods=["POST"])
@jwt_required()
def create_chat():
    data = request.json
    user_id = get_jwt_identity()

    prompt = data.get("title")
    if not prompt:
        return jsonify({"error": "Le titre/prompt est requis"}), 400

    # Créer le chat avec le titre utilisateur
    chat = Chat(title=prompt, user_id=user_id)
    db.session.add(chat)
    db.session.commit()  # Commit pour avoir l'ID si besoin

    user_msg = Message(chat_id=chat.id, sender="user", content=prompt)
    db.session.add(user_msg)
    db.session.commit()

    return jsonify({
        "chat_id": chat.id,
        "title": chat.title,
        "created_at": chat.created_at
    }), 201


@chat_bp.route("/chat", methods=["GET"])
@jwt_required()
def list_chats():
    user_id = get_jwt_identity()
    chats = Chat.query.filter_by(user_id=user_id).all()
    return jsonify([{"id": c.id, "title": c.title} for c in chats])

@chat_bp.route("/chat/<int:chat_id>", methods=["GET"])
@jwt_required()
def get_chat(chat_id):
    chat = Chat.query.get_or_404(chat_id)
    messages = Message.query.filter_by(chat_id=chat.id).all()
    return jsonify({
        "id": chat.id,
        "title": chat.title,
        "messages": [{"id": m.id, "sender": m.sender, "content": m.content} for m in messages]
    })

@chat_bp.route("/chat/<int:chat_id>", methods=["DELETE"])
@jwt_required()
def delete_chat(chat_id):
    chat = Chat.query.get_or_404(chat_id)
    db.session.delete(chat)
    db.session.commit()
    return jsonify({"message": "Chat deleted"})


@chat_bp.route("/chat/<int:chat_id>", methods=["PUT"])
@jwt_required()
def update_chat(chat_id):
    user_id = get_jwt_identity()
    chat = Chat.query.filter_by(id=chat_id, user_id=user_id).first_or_404()
    data = request.json
    new_title = data.get("title")
    if not new_title:
        return jsonify({"error": "Title is required"}), 400

    chat.title = new_title
    db.session.commit()
    return jsonify({"id": chat.id, "title": chat.title})


