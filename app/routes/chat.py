import os
import asyncio
from flask import Blueprint, request, jsonify, Response
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.ollama import ollama_service
from extensions import db
from app.models.chat import Chat

chat_bp = Blueprint("chat", __name__)

@chat_bp.route("/models", methods=["GET"])
@jwt_required()
def get_models():
    return jsonify(models=OLLAMA_MODELS)

@chat_bp.route('/prompt', methods=['POST'])
@jwt_required()
def create_prompt():
    data = request.get_json()
    user_id = get_jwt_identity()

    model = data.get("model")

    response = ollama_service(data['prompt'], model)

    new_prompt = Chat(
        user_id=user_id,
        prompt=data['prompt'],
        response=response
    )
    db.session.add(new_prompt)
    db.session.commit()

    return jsonify(
        id=new_prompt.id,
        prompt=new_prompt.prompt,
        model=model,
        response=new_prompt.response
    )


@chat_bp.route('/prompt/<int:prompt_id>', methods=['GET'])
@jwt_required()
def get_prompt(prompt_id):
    user_id = get_jwt_identity()
    prompt = Chat.query.filter_by(id=prompt_id, user_id=user_id).first()
    if not prompt:
        return jsonify({"error": "Prompt not found"}), 404
    return jsonify(
        id=prompt.id,
        prompt=prompt.prompt,
        response=prompt.response
    )


@chat_bp.route('/prompt/<int:prompt_id>', methods=['PUT'])
@jwt_required()
def update_prompt(prompt_id):
    data = request.get_json()
    user_id = get_jwt_identity()

    prompt = Chat.query.filter_by(id=prompt_id, user_id=user_id).first()
    if not prompt:
        return jsonify({"error": "Prompt not found"}), 404

    new_prompt_text = data.get("prompt")
    model = data.get("model")

    if new_prompt_text:
        prompt.prompt = new_prompt_text
        
        prompt.response = ollama_service(new_prompt_text, model)

    db.session.commit()
    return jsonify(
        id=prompt.id,
        prompt=prompt.prompt,
        model=model,
        response=prompt.response
    )


@chat_bp.route('/prompt/<int:prompt_id>', methods=['DELETE'])
@jwt_required()
def delete_prompt(prompt_id):
    user_id = get_jwt_identity()
    prompt = Chat.query.filter_by(id=prompt_id, user_id=user_id).first()
    if not prompt:
        return jsonify({"error": "Prompt not found"}), 404

    db.session.delete(prompt)
    db.session.commit()
    return jsonify({"message": "Prompt deleted successfully"})


@chat_bp.route('/prompts', methods=['GET'])
@jwt_required()
def get_all_prompts():
    user_id = get_jwt_identity()
    prompts = Chat.query.filter_by(user_id=user_id).order_by(Chat.id.desc()).all()

    result = []
    for p in prompts:
        result.append({
            "id": p.id,
            "prompt": p.prompt,
            "response": p.response
        })

    return jsonify(result)