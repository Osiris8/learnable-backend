import os
from flask import Blueprint,Response, request, stream_with_context, jsonify
from ollama import chat
from dotenv import load_dotenv
from flask_jwt_extended import jwt_required, get_jwt_identity
load_dotenv()
from extensions.database import db
from app.models.chat import Chat
from app.models.message import Message
from app.services.agent import AGENTS
from extensions.chroma import get_collection, embed_text
message_bp = Blueprint("message", __name__)


OLLAMA_MODELS = os.environ.get("OLLAMA_MODELS", "gemma3:1b").split(",")



def validate_model(model: str):
    if model not in OLLAMA_MODELS:
        raise ValueError(f"Model {model} is not allowed")

@message_bp.route("/chat/<int:chat_id>/messages", methods=["POST"])
@jwt_required()
def stream_chat(chat_id):
    user_id = get_jwt_identity()
    data = request.get_json()
    content = data.get("content")
    model = data.get("model", OLLAMA_MODELS[0])
    agent_type = data.get("agent", "assistant")

    validate_model(model)

    chat_obj = Chat.query.filter_by(id=chat_id, user_id=user_id).first_or_404()

   
    user_msg = Message(chat_id=chat_id, sender="user", content=content)
    db.session.add(user_msg)
    db.session.commit()

    user_msg_data = {
        "sender": "user",
        "chat_id": chat_id,
        "created_at": str(user_msg.created_at),
        "message_id": user_msg.id
    }

    collection = get_collection(chat_id)

    results = collection.query(
        query_embeddings=[embed_text(content)],
        n_results=5
    )
    system_prompt = AGENTS.get(agent_type) or ""
    context = ""
    if results.get("documents") and len(results["documents"]) > 0:
        context = "\n".join(results["documents"][0])
    if context:
        system_prompt += f"\n\nContext:\n{context}"

   

    def generate():
        full_response = ""
        stream = chat(
            model=model,
            messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": content}
    
    ],
            stream=True,
        )
        for chunk in stream:
            piece = chunk["message"]["content"]
            full_response += piece
            yield piece  

        ai_msg = Message(chat_id=chat_id, sender="ai", content=full_response)
        db.session.add(ai_msg)
        db.session.commit()

        
        ai_msg_data = {
            "sender": "ai",
            "chat_id": chat_id,
            "created_at": str(ai_msg.created_at),
            "message_id": ai_msg.id
        }

        collection.add(
        documents=[content, full_response],
        embeddings=[embed_text(content), embed_text(full_response)],
        metadatas=[
                {
                    "sender": "user",
                    "chat_id": chat_id,
                    "created_at": user_msg_data["created_at"],
                    "message_id": user_msg_data["message_id"]
                },
                {
                    "sender": "ai",
                    "chat_id": chat_id,
                    "created_at": ai_msg_data["created_at"],
                    "message_id": ai_msg_data["message_id"]
                }
            ],
            ids=[f"user_{user_msg_data['message_id']}", f"ai_{ai_msg_data['message_id']}"]
    )

    return Response(stream_with_context(generate()), mimetype="text/plain")


@message_bp.route("/chat/<int:chat_id>/first-message", methods=["GET"])
@jwt_required()
def stream_chat_first(chat_id):
    user_id = get_jwt_identity()
    chat_obj = Chat.query.filter_by(id=chat_id, user_id=user_id).first_or_404()
    model = chat_obj.model
    validate_model(model)

    

    
    agent_type = chat_obj.agent
    user_msg = Message.query.filter_by(chat_id=chat_id).first_or_404()
    user_content = user_msg.content
  
    collection = get_collection(chat_id)

    system_prompt = AGENTS.get(agent_type) or ""
  
   

   

    def generate():
        full_response = ""
        stream = chat(
            model=model,
            messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_content}
    
    ],
            stream=True,
        )
        for chunk in stream:
            piece = chunk["message"]["content"]
            full_response += piece
            yield piece  
        existing_ai = Message.query.filter_by(chat_id=chat_id, sender="ai").first()
        if not existing_ai:
            ai_msg = Message(chat_id=chat_id, sender="ai", content=full_response)
            db.session.add(ai_msg)
            db.session.commit()
           
        

        
            ai_msg_data = {
                "sender": "ai",
                "chat_id": chat_id,
                "created_at": str(ai_msg.created_at),
                "message_id": ai_msg.id
            }

            collection.add(
            documents=[full_response],
            embeddings=[embed_text(full_response)],
            metadatas=[
                
                    {
                        "sender": "ai",
                        "chat_id": chat_id,
                        "created_at": ai_msg_data["created_at"],
                        "message_id": ai_msg_data["message_id"]
                    }
                ],
                ids=[f"ai_{ai_msg_data['message_id']}"]
        )
       


    return Response(stream_with_context(generate()), mimetype="text/plain")


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
