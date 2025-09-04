
import os
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.ollama import ollama_service
from extensions.database import db
from app.models.chat import Chat
from app.models.message import Message
from app.services.agent import agents
from extensions.chroma import get_collection, embed_text
message_bp = Blueprint("messages", __name__)

@message_bp.route("/chat/<int:chat_id>/messages", methods=["POST"])
@jwt_required()
def send_message(chat_id):
    user_id = get_jwt_identity()
    data = request.json
    content = data.get("content")
    agent_type = data.get("agent", "assistant")
    model = data.get("model", "gpt-oss:20b")

    if not content:
        return jsonify({"error": "content is required"}), 400

   
    chat_obj = Chat.query.filter_by(id=chat_id, user_id=user_id).first_or_404()

   
    user_msg = Message(chat_id=chat_id, sender="user", content=content)
    db.session.add(user_msg)
    db.session.commit()

    agent_fn = agents.get(agent_type)
    if not agent_fn:
        return jsonify({"error": f"Agent '{agent_type}' not found"}), 400
    
    collection = get_collection(chat_id)

    results = collection.query(
        query_embeddings=[embed_text(content)],
        n_results=5
    )

    context = ""
    if results.get("documents") and len(results["documents"]) > 0:
        context = "\n".join(results["documents"][0])

    try:
        ai_content = agent_fn(
            f"The last question of the user (context): {context}\n"
            f"The user question: {content}\n"
            "Answer consistently with history.",
            model=model
        )
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


    ai_msg = Message(chat_id=chat_id, sender="ai", content=ai_content)
    db.session.add(ai_msg)
    db.session.commit()

    collection.add(
        documents=[content, ai_content],
        embeddings=[embed_text(content), embed_text(ai_content)],
        metadatas=[
            {
                "sender": "user",
                "chat_id": chat_id,
                "created_at": str(user_msg.created_at),
                "message_id": user_msg.id
            },
            {
                "sender": "ai",
                "chat_id": chat_id,
                "created_at": str(ai_msg.created_at),
                "message_id": ai_msg.id
            }
        ],
        ids=[f"user_{user_msg.id}", f"ai_{ai_msg.id}"]
    )
    return jsonify({
        "content": ai_msg.content or "",
        "agent": agent_type,
        "model": model
    }), 201


@message_bp.route("/chat/<int:chat_id>/messages", methods=["GET"])
@jwt_required()
def get_messages(chat_id):
    messages = (
        Message.query
        .filter_by(chat_id=chat_id)
        .order_by(Message.created_at.asc()) 
        .all()
    )
    return jsonify([
        {
            "id": m.id,
            "sender": m.sender,
            "content": m.content,
            "created_at": m.created_at.isoformat()
        }
        for m in messages
    ])




