from flask import Blueprint, request, jsonify
from models.prompt import Prompt

prompt_bp = Blueprint('prompt', __name__)

@prompt_bp.route('/', methods=['GET'])
def get_prompts():
    category = request.args.get('category')
    
    if category:
        prompts = Prompt.get_by_category(category)
    else:
        prompts = Prompt.get_all()
    
    return jsonify(prompts)

@prompt_bp.route('/<int:prompt_id>', methods=['GET'])
def get_prompt(prompt_id):
    prompt = Prompt.get_by_id(prompt_id)
    if prompt is None:
        return jsonify({"error": "Prompt not found"}), 404
    return jsonify(prompt)

@prompt_bp.route('/', methods=['POST'])
def create_prompt():
    data = request.get_json()
    
    if not data or 'content' not in data:
        return jsonify({"error": "Content is required"}), 400
    
    content = data.get('content')
    category = data.get('category')
    
    prompt_id = Prompt.create(content, category)
    return jsonify({"id": prompt_id, "message": "Prompt created successfully"}), 201

@prompt_bp.route('/<int:prompt_id>', methods=['PUT'])
def update_prompt(prompt_id):
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    content = data.get('content')
    category = data.get('category')
    
    success = Prompt.update(prompt_id, content, category)
    
    if not success:
        return jsonify({"error": "Prompt not found"}), 404
    
    return jsonify({"message": "Prompt updated successfully"})

@prompt_bp.route('/<int:prompt_id>', methods=['DELETE'])
def delete_prompt(prompt_id):
    success = Prompt.delete(prompt_id)
    
    if not success:
        return jsonify({"error": "Prompt not found"}), 404
    
    return jsonify({"message": "Prompt deleted successfully"})

@prompt_bp.route('/categories', methods=['GET'])
def get_categories():
    db = Prompt.get_db()
    categories = db.execute('SELECT DISTINCT category FROM prompts WHERE category IS NOT NULL').fetchall()
    return jsonify([category['category'] for category in categories]) 