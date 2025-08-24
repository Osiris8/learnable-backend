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

    # Résumé du prompt par l'IA pour le titre
    try:
        ai_summary = ollama_service(
            f"Résume en quelques mots cette demande de l'utilisateur : {prompt}",
            model="gemma3:1b"
        )

        ai_content = ollama_service(f"""
      
Rules to follow exactly:

If the words (course, lesson, learning) are found in the user’s request, then:

Generate a complete course: introduction, structured outline, detailed explanations, summaries, solved exercises, quizzes, and a final project.

If the user’s request is a normal question (not a full learning request), respond in a simple and direct way, like a regular chat assistant.

Always remain clear, concise, and helpful.

Here is the user’s request:
"{prompt}"
                           
        """, model="gemma3:1b")  # réponse IA 
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    # Créer le chat avec titre utilisateur et résumé IA
    chat = Chat(
        title=prompt,
        title_ai_summarize=ai_summary,
        user_id=user_id
    )
    db.session.add(chat)
    db.session.commit()  # Commit pour obtenir l'ID

    # Enregistrer le premier message utilisateur
    user_msg = Message(chat_id=chat.id, sender="user", content=prompt)
    db.session.add(user_msg)

    # Enregistrer le premier message de l'IA
    ai_msg = Message(chat_id=chat.id, sender="ai", content=ai_content)
    db.session.add(ai_msg)

    db.session.commit()

    return jsonify({
        "chat_id": chat.id,
        "title": chat.title,
        "title_ai_summarize": chat.title_ai_summarize,
        "created_at": chat.created_at,
        "messages": [
            {"id": user_msg.id, "sender": user_msg.sender, "content": user_msg.content},
            {"id": ai_msg.id, "sender": ai_msg.sender, "content": ai_msg.content}
        ]
    }), 201


@chat_bp.route("/chat", methods=["GET"])
@jwt_required()
def list_chats():
    user_id = get_jwt_identity()
    chats = Chat.query.filter_by(user_id=user_id).all()
    return jsonify([{"id": c.id, "title": c.title, "title_ai_summarize":c.title_ai_summarize} for c in chats])

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

