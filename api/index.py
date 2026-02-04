import os
import sys

# Add parent directory to path so we can import src modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, jsonify

app = Flask(__name__)

# Load config
try:
    from src.config.config import Config
    app.config.from_object(Config)
except Exception as e:
    print(f"Config Error: {e}")

# Register blueprints with error handling
try:
    from src.routes.api_routes import auth_bp, dana_bp, user_bp, disburse_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(dana_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(disburse_bp)
except Exception as e:
    print(f"Blueprint Error: {e}")

@app.route('/')
def health_check():
    try:
        from src.services.health_service import HealthService
        return HealthService().getHealthStatus()
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Health check failed: {str(e)}",
            "database": "not connected"
        }), 500

@app.route('/api/health')
def simple_health():
    """Simple health check without database"""
    return jsonify({
        "status": "ok",
        "service": "be-dana",
        "database_url_set": bool(os.getenv('DATABASE_URL') or os.getenv('POSTGRES_URL'))
    })

# Global Error Handlers
@app.errorhandler(400)
def bad_request(e):
    return jsonify({"status_code": 400, "status": "error", "message": "Bad Request"}), 400

@app.errorhandler(401)
def unauthorized(e):
    return jsonify({"status_code": 401, "status": "error", "message": "Unauthorized"}), 401

@app.errorhandler(403)
def forbidden(e):
    return jsonify({"status_code": 403, "status": "error", "message": "Forbidden"}), 403

@app.errorhandler(404)
def not_found(e):
    return jsonify({"status_code": 404, "status": "error", "message": "Not Found"}), 404

@app.errorhandler(500)
def internal_server_error(e):
    return jsonify({"status_code": 500, "status": "error", "message": str(e)}), 500

# Required for Vercel
if __name__ == '__main__':
    app.run(debug=True)
