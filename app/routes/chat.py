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
        return jsonify({"error": "The title/prompt is required"}), 400
    
    
    allowed_models = os.getenv("OLLAMA_MODELS", "gemma3:1b").split(",")

   
    model = data.get("model", "gemma3:1b")

   
    if model not in allowed_models:
        return jsonify({"error": f"The model '{model}' is not allowed."}), 400


    try:
        ai_summary = ollama_service(
            f"Summarize in 3 words the question of user : {prompt}",
            model=model
        )

        ai_content = ollama_service(f"""
      
Rules to follow exactly:

If the words (course, lesson, learning) are found in the user’s request, then:

Generate a complete course: introduction, structured outline, detailed explanations, summaries, solved exercises, quizzes, and a final project.

If the user’s request is a normal question (not a full learning request), respond in a simple and direct way, like a regular chat assistant.

Always remain clear, concise, and helpful.

Here is the user’s request:
"{prompt}"
                           
        """, model=model) 
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    
    chat = Chat(
        title=prompt,
        title_ai_summarize=ai_summary,
        user_id=user_id
    )
    db.session.add(chat)
    db.session.commit() 


    user_msg = Message(chat_id=chat.id, sender="user", content=prompt)
    db.session.add(user_msg)

    
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


    Message.query.filter_by(chat_id=chat.id).delete()

    
    db.session.delete(chat)
    db.session.commit()

    return jsonify({"message": "Chat and its messages deleted"})


@chat_bp.route("/chat/<int:chat_id>", methods=["PUT"])
@jwt_required()
def update_chat(chat_id):
    user_id = get_jwt_identity()
    chat = Chat.query.filter_by(id=chat_id, user_id=user_id).first_or_404()
    data = request.json
    new_title = data.get("title")
    if not new_title:
        return jsonify({"error": "Title is required"}), 400

    chat.title_ai_summarize = new_title
    db.session.commit()
    return jsonify({"id": chat.id, "title": chat.title_ai_summarize})


@chat_bp.route("/navbar-summaries", methods=["GET"])
@jwt_required()
def get_navbar_summaries():
    user_id = get_jwt_identity() 
    
    chats = Chat.query.filter_by(user_id=user_id).order_by(Chat.created_at.desc()).all()
    
    summaries = [
        {
            "id": chat.id,
            "title_summary": chat.title_ai_summarize or chat.title
        }
        for chat in chats
    ]
    
    return jsonify(summaries)