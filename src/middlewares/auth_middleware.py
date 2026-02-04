from functools import wraps
from flask import request, jsonify, g
from src.config.config import Config
import jwt


def token_required(f):
    """
    Decorator untuk memvalidasi JWT token
    Setelah validasi, user info akan tersedia di g.current_user
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        # Ambil token dari header Authorization
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]

        if not token:
            return jsonify({
                "status_code": 401,
                "status": "error",
                "message": "Unauthorized: Token is missing"
            }), 401

        try:
            # Decode dan validasi JWT token
            jwtSecret = getattr(Config, 'JWT_SECRET', 'your-secret-key-change-in-production')
            payload = jwt.decode(token, jwtSecret, algorithms=['HS256'])

            # Set current user di flask g object
            g.current_user = {
                'user_id': payload.get('user_id'),
                'email': payload.get('email'),
                'muzaki_id': payload.get('muzaki_id'),
                'type': payload.get('type')
            }

        except jwt.ExpiredSignatureError:
            return jsonify({
                "status_code": 401,
                "status": "error",
                "message": "Unauthorized: Token has expired"
            }), 401

        except jwt.InvalidTokenError as e:
            return jsonify({
                "status_code": 401,
                "status": "error",
                "message": f"Unauthorized: Invalid token - {str(e)}"
            }), 401

        return f(*args, **kwargs)

    return decorated


def optional_token(f):
    """
    Decorator untuk token optional
    Jika token ada dan valid, set g.current_user
    Jika tidak ada atau invalid, tetap lanjutkan tanpa user info
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        g.current_user = None

        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]

        if token:
            try:
                jwtSecret = getattr(Config, 'JWT_SECRET', 'your-secret-key-change-in-production')
                payload = jwt.decode(token, jwtSecret, algorithms=['HS256'])

                g.current_user = {
                    'user_id': payload.get('user_id'),
                    'email': payload.get('email'),
                    'muzaki_id': payload.get('muzaki_id'),
                    'type': payload.get('type')
                }
            except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
                # Token invalid, tapi tetap lanjutkan
                pass

        return f(*args, **kwargs)

    return decorated


def admin_required(f):
    """
    Decorator untuk endpoint yang memerlukan admin access
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]

        if not token:
            return jsonify({
                "status_code": 401,
                "status": "error",
                "message": "Unauthorized: Token is missing"
            }), 401

        try:
            jwtSecret = getattr(Config, 'JWT_SECRET', 'your-secret-key-change-in-production')
            payload = jwt.decode(token, jwtSecret, algorithms=['HS256'])

            # Cek apakah user adalah admin
            userType = payload.get('type')
            if userType not in ['admin', 'superadmin']:
                return jsonify({
                    "status_code": 403,
                    "status": "error",
                    "message": "Forbidden: Admin access required"
                }), 403

            g.current_user = {
                'user_id': payload.get('user_id'),
                'email': payload.get('email'),
                'muzaki_id': payload.get('muzaki_id'),
                'type': userType
            }

        except jwt.ExpiredSignatureError:
            return jsonify({
                "status_code": 401,
                "status": "error",
                "message": "Unauthorized: Token has expired"
            }), 401

        except jwt.InvalidTokenError as e:
            return jsonify({
                "status_code": 401,
                "status": "error",
                "message": f"Unauthorized: Invalid token - {str(e)}"
            }), 401

        return f(*args, **kwargs)

    return decorated
