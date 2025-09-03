
import os
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.ollama import ollama_service
from extensions import db, get_collection
from app.models.chat import Chat
from app.models.message import Message
from app.services.agent import agents
message_bp = Blueprint("messages", __name__)

@message_bp.route("/chat/<int:chat_id>/messages", methods=["POST"])
@jwt_required()
def send_message(chat_id):
    user_id = get_jwt_identity()
    data = request.json
    content = data.get("content")
    agent_type = data.get("agent", "assistant")
    model = data.get("model", "gemma3:1b")

    if not content:
        return jsonify({"error": "content is required"}), 400
    

    allowed_models = os.getenv("OLLAMA_MODELS", "gemma3:1b").split(",")

   
    

   
    if model not in allowed_models:
        return jsonify({"error": f"The model '{model}' is not allowed."}), 400

   
    chat_obj = Chat.query.filter_by(id=chat_id, user_id=user_id).first_or_404()

   
    user_msg = Message(chat_id=chat_id, sender="user", content=content)
    db.session.add(user_msg)
    db.session.commit()

    agent_fn = agents.get(agent_type)
    if not agent_fn:
        return jsonify({"error": f"Agent '{agent_type}' not found"}), 400
    
    collection = get_collection(chat_id)

    results = collection.query(
        query_texts=[content],
        n_results=5
    )

    context = "\n".join(results["documents"][0]) if results["documents"] else ""

    try:
        ai_content = agent_fn(f"The last question of the user : {context} The user question: {content} Answers consistently with history.",
            model=model)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


    ai_msg = Message(chat_id=chat_id, sender="ai", content=ai_content)
    db.session.add(ai_msg)
    db.session.commit()

    collection.add(
        documents=[content, ai_content],
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




