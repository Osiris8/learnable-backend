import os
import asyncio
from flask import Blueprint, request, jsonify, Response
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.ollama import ollama_service
from extensions.database import db
from app.models.chat import Chat
from app.models.message import Message
from app.services.agent import agents
from extensions.chroma import get_collection, embed_text


chat_bp = Blueprint("chats", __name__)

@chat_bp.route("/chat", methods=["POST"])
@jwt_required()
def create_chat():
    data = request.json
    user_id = get_jwt_identity()

    prompt = data.get("title")
    agent_type = data.get("agent", "assistant")
    model = data.get("model", "gpt-oss:20b")

    if not prompt:
        return jsonify({"error": "The title/prompt is required"}), 400

 

    
    agent_fn = agents.get(agent_type)
    if not agent_fn:
        return jsonify({"error": f"Agent '{agent_type}' not found"}), 400

    try:

        
        ai_content = agent_fn(prompt, model)

    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    
    chat = Chat(
        title=prompt,
       
        agent=agent_type,
        user_id=user_id
    )
    db.session.add(chat)
    db.session.commit()

    user_msg = Message(chat_id=chat.id, sender="user", content=prompt)
    db.session.add(user_msg)

    ai_msg = Message(chat_id=chat.id, sender="ai", content=ai_content)
    db.session.add(ai_msg)

    db.session.commit()
    collection = get_collection(chat.id)
    collection.add(
    documents=[prompt, ai_content],
    embeddings=[embed_text(prompt), embed_text(ai_content)],
    metadatas=[
        {
            "sender": "user",
            "chat_id": chat.id,
            "created_at": str(user_msg.created_at),
            "message_id": user_msg.id,
        },
        {
            "sender": "ai",
            "chat_id": chat.id,
            "created_at": str(ai_msg.created_at),
            "message_id": ai_msg.id,
        },
    ],
    ids=[f"user_{user_msg.id}", f"ai_{ai_msg.id}"]  
    )


    return jsonify({
        "chat_id": chat.id,
        "title": chat.title,
      
        "created_at": chat.created_at,
        "agent": agent_type,
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
        "agent": chat.agent,
        "messages": [{"id": m.id, "sender": m.sender, "content": m.content} for m in messages]
    })

@chat_bp.route("/chat/<int:chat_id>", methods=["DELETE"])
@jwt_required()
def delete_chat(chat_id):
    chat = Chat.query.get_or_404(chat_id)


    Message.query.filter_by(chat_id=chat.id).delete()

    
    db.session.delete(chat)
    db.session.commit()

    try:
        collection = get_collection(chat.id)
        
        collection.delete(where={"chat_id": chat.id})
        
       
    except Exception as e:
        
        print(f"Warning: could not delete ChromaDB collection: {e}")

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
            "title": chat.title
        }
        for chat in chats
    ]
    
    return jsonify(summaries)