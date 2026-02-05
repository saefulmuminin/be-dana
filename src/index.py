from flask import Flask, jsonify
from src.config.config import Config
from src.routes.api_routes import auth_bp, dana_bp, user_bp, disburse_bp, snap_bp
from src.services.health_service import HealthService

app = Flask(__name__)
app.config.from_object(Config)

# Register Core Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(dana_bp)
app.register_blueprint(user_bp)
app.register_blueprint(disburse_bp)

# Register SNAP API Blueprint (ASPI-mandated paths)
app.register_blueprint(snap_bp)

@app.route('/')
def health_check():
    return HealthService().getHealthStatus()

# Global Error Handlers (using error_status.md)
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

@app.errorhandler(422)
def unprocessable_entity(e):
    return jsonify({"status_code": 422, "status": "error", "message": "Unprocessable Entity"}), 422

@app.errorhandler(500)
def internal_server_error(e):
    return jsonify({"status_code": 500, "status": "error", "message": "Internal Server Error"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8899)
