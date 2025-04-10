from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from models import User, db
from logger import logger

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['POST'])
def login():
    if not request.is_json:
        logger.warning("Login attempt with non-JSON request")
        return jsonify({"msg": "Missing JSON in request"}), 400
    
    username = request.json.get('username', None)
    password = request.json.get('password', None)
    
    if not username or not password:
        logger.warning("Login attempt with missing credentials")
        return jsonify({"msg": "Missing username or password"}), 400
    
    user = User.query.filter_by(username=username).first()
    
    if user is None or not user.check_password(password):
        logger.warning(f"Failed login attempt for username: {username}")
        return jsonify({"msg": "Invalid username or password"}), 401
    
    logger.info(f"Successful login for user: {username}")
    access_token = create_access_token(identity=username)
    return jsonify(access_token=access_token, username=user.username, 
                  first_name=user.first_name, last_name=user.last_name), 200

@auth.route('/user', methods=['GET'])
@jwt_required()
def get_user():
    current_user = get_jwt_identity()
    logger.info(f"User profile request for: {current_user}")
    user = User.query.filter_by(username=current_user).first()
    
    if not user:
        logger.warning(f"User not found: {current_user}")
        return jsonify({"msg": "User not found"}), 404
    
    return jsonify(
        username=user.username,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name
    ), 200

def init_admin_user():
    """Create a default admin user if no users exist"""
    try:
        if User.query.count() == 0:
            admin_user = User(
                username='admin',
                email='admin@example.com',
                first_name='Admin',
                last_name='User'
            )
            admin_user.set_password('admin123')  # Should be changed in production
            db.session.add(admin_user)
            db.session.commit()
            logger.info("Created initial admin user")
    except Exception as e:
        logger.error("Failed to create admin user", exc_info=True) 