from flask import Blueprint, request, jsonify
from models.result import Result
from models.attack import Attack
from models.prompt import Prompt
from database.db_setup import get_db

result_bp = Blueprint('result', __name__)

@result_bp.route('/', methods=['GET'])
def get_results():
    attack_id = request.args.get('attack_id')
    category = request.args.get('category')
    
    if attack_id and category:
        # 同时按攻击ID和类别筛选
        results = Result.get_by_attack_and_category(attack_id, category)
    elif attack_id:
        # 只按攻击ID筛选
        results = Result.get_by_attack(attack_id)
    elif category:
        # 只按类别筛选
        results = Result.get_by_category(category)
    else:
        # 获取所有结果
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
    
    # 打印日志以便调试
    print(f"Updating result {result_id} with success_rating: {success_rating}")
    
    success = Result.update(result_id, model_response, success_rating)
    
    if not success:
        return jsonify({"error": "Result not found"}), 404
    
    # 获取更新后的结果
    updated_result = Result.get_by_id(result_id)
    
    return jsonify({"message": "Result updated successfully", "result": updated_result})

@result_bp.route('/<int:result_id>', methods=['DELETE'])
def delete_result(result_id):
    success = Result.delete(result_id)
    
    if not success:
        return jsonify({"error": "Result not found"}), 404
    
    return jsonify({"message": "Result deleted successfully"})

@result_bp.route('/batch-delete', methods=['POST'])
def batch_delete_results():
    data = request.get_json()
    
    if not data or 'result_ids' not in data or not isinstance(data['result_ids'], list):
        return jsonify({"error": "Result IDs list is required"}), 400
    
    result_ids = data.get('result_ids')
    
    if not result_ids:
        return jsonify({"error": "No result IDs provided"}), 400
    
    results = {
        "total": len(result_ids),
        "deleted": 0,
        "failed": 0
    }
    
    for result_id in result_ids:
        try:
            success = Result.delete(result_id)
            if success:
                results["deleted"] += 1
            else:
                results["failed"] += 1
        except Exception:
            results["failed"] += 1
    
    return jsonify({
        "message": f"批量删除完成。{results['deleted']} 个结果已删除，{results['failed']} 个删除失败。",
        "results": results
    })

@result_bp.route('/stats', methods=['GET'])
def get_stats():
    """
    Get statistics about jailbreak harmful scores
    """
    db = get_db()
    
    # Get overall stats
    total_results = db.execute('SELECT COUNT(*) as count FROM results').fetchone()['count']
    harmful_results = db.execute('SELECT COUNT(*) as count FROM results WHERE success_rating > 3').fetchone()['count']
    
    # Get stats by attack type
    attack_stats = db.execute('''
        SELECT a.id, a.name, a.algorithm_type, 
               COUNT(r.id) as total_attempts,
               SUM(CASE WHEN r.success_rating > 3 THEN 1 ELSE 0 END) as harmful_attempts,
               AVG(r.success_rating) as avg_harmful_score
        FROM attacks a
        LEFT JOIN results r ON a.id = r.attack_id
        GROUP BY a.id
    ''').fetchall()
    
    return jsonify({
        "total_results": total_results,
        "harmful_results": harmful_results,
        "harmful_rate": (harmful_results / total_results) if total_results > 0 else 0,
        "attack_stats": [dict(stat) for stat in attack_stats]
    }) 