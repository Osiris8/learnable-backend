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

    try:
        # 1️⃣ Résumé du prompt pour le titre
        ai_summary = ollama_service(
            f"Résume en quelques mots cette demande de l'utilisateur : {prompt}",
            model="gemma3:1b"
        )

        # 2️⃣ Détecter le type de chat : général ou plan d'apprentissage
        chat_type = ollama_service(
            f"""
            Ton role est d'enseigner des étudiants, des élèves et tous ceux qui souhaitent apprendre.
            Tu es un assistant intelligent pour les professionels en entreprise et aussi les particuliers
            Quand on fait appel à toi, on doit apprendre, débloquer des situations urgentes et non urgentes
            Tu es professeur d'unviversité et tu as tous les doctorats.
            L'utilisateur demande : "{prompt}".
            Analyse la demande de l'utilisateur. Si c'est une demande de cours, d'apprentissage, répond exactement :
            "course_request".
            Sinon comporte toi comme un chat GPT classique qui répond à la question de l'utilisateur.
            """,
            model="gemma3:1b"
        ).strip().lower()

        # 3️⃣ Générer le contenu selon le type
        if chat_type == "course_request":
            # Mode plan d'apprentissage complet
            ai_content = ollama_service(
                f"""
                L'utilisateur veut apprendre : "{prompt}".
                Fournis un plan d'apprentissage complet et structuré :
                1. Introduction
                2. Objectifs clairs
                3. Chapitres détaillés avec titres et sous-sections
                
                4. Résumé de chaque chapitre
                5. Exercices avec corrigés par chapitre
                6. Suggestions de mini-projets.
                """,
                model="gemma3:1b"
            )
        else:
            # Mode chat général
            ai_content = ollama_service(prompt, model="gemma3:1b")

    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    # 4️⃣ Créer le chat
    chat = Chat(
        title=prompt,
        title_ai_summarize=ai_summary,
        user_id=user_id
    )
    db.session.add(chat)
    db.session.commit()  # pour obtenir l'ID

    # 5️⃣ Enregistrer les messages
    user_msg = Message(chat_id=chat.id, sender="user", content=prompt)
    db.session.add(user_msg)

    ai_msg = Message(chat_id=chat.id, sender="ai", content=ai_content)
    db.session.add(ai_msg)

    db.session.commit()

    # 6️⃣ Retour JSON
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


