from flask import Blueprint, request, jsonify
from extensions.database import db
from app.models.user import User
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/signup', methods=['POST'])
def register():
    data = request.get_json()
    user = User(
    firstname=data['firstname'], 
    lastname=data['lastname'], 
    email=data['email'])
    user.set_password(data['password'])
 

    db.session.add(user)
    db.session.commit()
    return jsonify(msg="User created"), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data['email']).first()
    if user and user.check_password(data['password']):
        token = create_access_token(identity=str(user.id))
        return jsonify(access_token = token)
    return jsonify(msg="Unvalid user informations"), 401




@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    return jsonify(msg="logout successfully"), 200




@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify(msg="User not found"), 404

    return jsonify(
        user={
            "firstname": f"{user.firstname}",
            "lastname":f"{user.lastname}",
            "email": user.email
        }
    )
