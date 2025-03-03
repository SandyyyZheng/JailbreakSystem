from flask import Blueprint, request, jsonify
from models.result import Result
from models.attack import Attack
from models.prompt import Prompt
from database.db_setup import get_db

result_bp = Blueprint('result', __name__)

@result_bp.route('/', methods=['GET'])
def get_results():
    attack_id = request.args.get('attack_id')
    
    if attack_id:
        results = Result.get_by_attack(attack_id)
    else:
        results = Result.get_all()
    
    return jsonify(results)

@result_bp.route('/<int:result_id>', methods=['GET'])
def get_result(result_id):
    result = Result.get_by_id(result_id)
    if result is None:
        return jsonify({"error": "Result not found"}), 404
    return jsonify(result)

@result_bp.route('/', methods=['POST'])
def create_result():
    data = request.get_json()
    
    if not data or 'attack_id' not in data or 'original_prompt' not in data or 'jailbreak_prompt' not in data:
        return jsonify({"error": "Attack ID, original prompt, and jailbreak prompt are required"}), 400
    
    attack_id = data.get('attack_id')
    prompt_id = data.get('prompt_id')
    original_prompt = data.get('original_prompt')
    jailbreak_prompt = data.get('jailbreak_prompt')
    model_response = data.get('model_response')
    success_rating = data.get('success_rating')
    
    # Validate attack_id
    attack = Attack.get_by_id(attack_id)
    if attack is None:
        return jsonify({"error": "Attack not found"}), 404
    
    # Validate prompt_id if provided
    if prompt_id:
        prompt = Prompt.get_by_id(prompt_id)
        if prompt is None:
            return jsonify({"error": "Prompt not found"}), 404
    
    result_id = Result.create(attack_id, prompt_id, original_prompt, jailbreak_prompt, model_response, success_rating)
    return jsonify({"id": result_id, "message": "Result created successfully"}), 201

@result_bp.route('/<int:result_id>', methods=['PUT'])
def update_result(result_id):
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    model_response = data.get('model_response')
    success_rating = data.get('success_rating')
    
    success = Result.update(result_id, model_response, success_rating)
    
    if not success:
        return jsonify({"error": "Result not found"}), 404
    
    return jsonify({"message": "Result updated successfully"})

@result_bp.route('/<int:result_id>', methods=['DELETE'])
def delete_result(result_id):
    success = Result.delete(result_id)
    
    if not success:
        return jsonify({"error": "Result not found"}), 404
    
    return jsonify({"message": "Result deleted successfully"})

@result_bp.route('/stats', methods=['GET'])
def get_stats():
    """
    Get statistics about jailbreak success rates
    """
    db = get_db()
    
    # Get overall stats
    total_results = db.execute('SELECT COUNT(*) as count FROM results').fetchone()['count']
    successful_results = db.execute('SELECT COUNT(*) as count FROM results WHERE success_rating > 7').fetchone()['count']
    
    # Get stats by attack type
    attack_stats = db.execute('''
        SELECT a.id, a.name, a.algorithm_type, 
               COUNT(r.id) as total_attempts,
               SUM(CASE WHEN r.success_rating > 7 THEN 1 ELSE 0 END) as successful_attempts,
               AVG(r.success_rating) as avg_success_rating
        FROM attacks a
        LEFT JOIN results r ON a.id = r.attack_id
        GROUP BY a.id
    ''').fetchall()
    
    return jsonify({
        "total_results": total_results,
        "successful_results": successful_results,
        "success_rate": (successful_results / total_results) if total_results > 0 else 0,
        "attack_stats": [dict(stat) for stat in attack_stats]
    }) 