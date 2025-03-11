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

@prompt_bp.route('/batch-delete', methods=['POST'])
def batch_delete_prompts():
    data = request.get_json()
    
    if not data or 'prompt_ids' not in data or not isinstance(data['prompt_ids'], list):
        return jsonify({"error": "Prompt IDs list is required"}), 400
    
    prompt_ids = data.get('prompt_ids')
    
    if not prompt_ids:
        return jsonify({"error": "No prompt IDs provided"}), 400
    
    results = {
        "total": len(prompt_ids),
        "deleted": 0,
        "failed": 0
    }
    
    for prompt_id in prompt_ids:
        try:
            success = Prompt.delete(prompt_id)
            if success:
                results["deleted"] += 1
            else:
                results["failed"] += 1
        except Exception:
            results["failed"] += 1
    
    return jsonify({
        "message": f"Batch delete completed. {results['deleted']} prompts deleted, {results['failed']} failed.",
        "results": results
    })

@prompt_bp.route('/categories', methods=['GET'])
def get_categories():
    db = Prompt.get_db()
    categories = db.execute('SELECT DISTINCT category FROM prompts WHERE category IS NOT NULL').fetchall()
    return jsonify([category['category'] for category in categories]) 