import os
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.ollama import ollama_service
from extensions import db
from app.models.chat import Chat
from app.models.message import Message

message_bp = Blueprint("messages", __name__)

@message_bp.route("/chat/<int:chat_id>/messages", methods=["POST"])
@jwt_required()
def send_message(chat_id):
    user_id = get_jwt_identity()
    data = request.json
    content = data.get("content")

    if not content:
        return jsonify({"error": "Le contenu est requis"}), 400

    # Vérifier que le chat existe
    chat_obj = Chat.query.filter_by(id=chat_id, user_id=user_id).first_or_404()

    # Enregistrer le message utilisateur
    user_msg = Message(chat_id=chat_id, sender="user", content=content)
    db.session.add(user_msg)
    db.session.commit()

    # Générer la réponse IA via Ollama
    try:
        ai_content = ollama_service(
            f"The user question: {content}",
            model="gemma3:1b"
        )
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    # Enregistrer la réponse IA
    ai_msg = Message(chat_id=chat_id, sender="ai", content=ai_content)
    db.session.add(ai_msg)
    db.session.commit()

    # Retourner uniquement la réponse IA pour le frontend
    return jsonify({
        "content": ai_msg.content or ""
    }), 201


@message_bp.route("/chat/<int:chat_id>/messages", methods=["GET"])
@jwt_required()
def get_messages(chat_id):
    messages = (
        Message.query
        .filter_by(chat_id=chat_id)
        .order_by(Message.created_at.asc())  # ordre croissant
        .all()
    )
    return jsonify([
        {
            "id": m.id,
            "sender": m.sender,
            "content": m.content,
            "created_at": m.created_at.isoformat()  # format JSON
        }
        for m in messages
    ])




