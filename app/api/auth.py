from flask import Blueprint, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from app.models.user import User
from app.utils.auth import generate_token
from app.utils.logger import logger
from app import db

auth = Blueprint('auth', __name__)

@auth.route('/register', methods=['POST'])
def register():
    try:
        data = request.json
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'error': 'Username already exists'}), 400

        user = User(
            username=data['username'],
            email=data['email']
        )
        user.set_password(data['password'])
        user.generate_api_key()
        
        db.session.add(user)
        db.session.commit()

        logger.info(f"New user registered: {user.username}")
        return jsonify({
            'message': 'Registration successful',
            'api_key': user.api_key
        })

    except Exception as e:
        logger.error(f"Registration failed: {str(e)}")
        return jsonify({'error': 'Registration failed'}), 500

@auth.route('/login', methods=['POST'])
def login():
    try:
        data = request.json
        user = User.query.filter_by(username=data['username']).first()
        
        if user and user.check_password(data['password']):
            login_user(user)
            token = generate_token(user)
            
            logger.info(f"User logged in: {user.username}")
            return jsonify({
                'token': token,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'role': user.role
                }
            })
            
        return jsonify({'error': 'Invalid credentials'}), 401

    except Exception as e:
        logger.error(f"Login failed: {str(e)}")
        return jsonify({'error': 'Login failed'}), 500

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return jsonify({'message': 'Logged out successfully'})

@auth.route('/profile')
@login_required
def profile():
    return jsonify({
        'username': current_user.username,
        'email': current_user.email,
        'role': current_user.role
    })

@auth.route('/reset-api-key', methods=['POST'])
@login_required
def reset_api_key():
    try:
        new_api_key = current_user.generate_api_key()
        db.session.commit()
        
        logger.info(f"API key reset for user: {current_user.username}")
        return jsonify({'api_key': new_api_key})
        
    except Exception as e:
        logger.error(f"API key reset failed: {str(e)}")
        return jsonify({'error': 'Failed to reset API key'}), 500 