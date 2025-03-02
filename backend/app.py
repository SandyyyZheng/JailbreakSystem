from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
from database.db_setup import init_db
from controllers.attack_controller import attack_bp
from controllers.prompt_controller import prompt_bp
from controllers.result_controller import result_bp

# Initialize Flask app
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Configuration
app.config['DATABASE'] = os.path.join(os.path.dirname(__file__), 'database', 'jailbreak.db')
app.config['SECRET_KEY'] = 'your-secret-key-here'  # Change this in production

# Register blueprints
app.register_blueprint(attack_bp, url_prefix='/api/attacks')
app.register_blueprint(prompt_bp, url_prefix='/api/prompts')
app.register_blueprint(result_bp, url_prefix='/api/results')

# Initialize database
with app.app_context():
    init_db()

@app.route('/')
def index():
    return jsonify({"message": "Jailbreak System API is running"})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001) 