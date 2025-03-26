from flask import Blueprint, request, jsonify
from models.attack import Attack
from utils.jailbreak_algorithms import apply_jailbreak
from utils.llm_service import llm_service
import json
import asyncio

attack_bp = Blueprint('attack', __name__)

@attack_bp.route('/', methods=['GET'])
def get_attacks():
    attacks = Attack.get_all()
    return jsonify(attacks)

@attack_bp.route('/<int:attack_id>', methods=['GET'])
def get_attack(attack_id):
    attack = Attack.get_by_id(attack_id)
    if attack is None:
        return jsonify({"error": "Attack not found"}), 404
    return jsonify(attack)

@attack_bp.route('/', methods=['POST'])
def create_attack():
    data = request.get_json()
    
    if not data or 'name' not in data or 'algorithm_type' not in data:
        return jsonify({"error": "Name and algorithm_type are required"}), 400
    
    name = data.get('name')
    description = data.get('description')
    algorithm_type = data.get('algorithm_type')
    parameters = data.get('parameters')
    
    # 调试输出
    print(f"DEBUG: Creating attack with name: {name}, algorithm_type: {algorithm_type}")
    print(f"DEBUG: parameters: {parameters}")
    
    attack_id = Attack.create(name, description, algorithm_type, parameters)
    return jsonify({"id": attack_id, "message": "Attack created successfully"}), 201

@attack_bp.route('/<int:attack_id>', methods=['PUT'])
def update_attack(attack_id):
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    name = data.get('name')
    description = data.get('description')
    algorithm_type = data.get('algorithm_type')
    parameters = data.get('parameters')
    
    success = Attack.update(attack_id, name, description, algorithm_type, parameters)
    
    if not success:
        return jsonify({"error": "Attack not found"}), 404
    
    return jsonify({"message": "Attack updated successfully"})

@attack_bp.route('/<int:attack_id>', methods=['DELETE'])
def delete_attack(attack_id):
    success = Attack.delete(attack_id)
    
    if not success:
        return jsonify({"error": "Attack not found"}), 404
    
    return jsonify({"message": "Attack deleted successfully"})

@attack_bp.route('/batch-delete', methods=['POST'])
def batch_delete_attacks():
    data = request.get_json()
    
    if not data or 'attack_ids' not in data or not isinstance(data['attack_ids'], list):
        return jsonify({"error": "Attack IDs list is required"}), 400
    
    attack_ids = data.get('attack_ids')
    
    if not attack_ids:
        return jsonify({"error": "No attack IDs provided"}), 400
    
    results = {
        "total": len(attack_ids),
        "deleted": 0,
        "failed": 0
    }
    
    for attack_id in attack_ids:
        try:
            success = Attack.delete(attack_id)
            if success:
                results["deleted"] += 1
            else:
                results["failed"] += 1
        except Exception:
            results["failed"] += 1
    
    return jsonify({
        "message": f"Batch deletion completed. {results['deleted']} attacks deleted, {results['failed']} failed.",
        "results": results
    })

@attack_bp.route('/execute', methods=['POST'])
async def execute_attack():
    """
    Execute a jailbreak attack on a prompt using real LLM APIs
    """
    data = request.get_json()
    
    if not data or 'attack_id' not in data or 'prompt' not in data:
        return jsonify({"error": "Attack ID and prompt are required"}), 400
    
    attack_id = data.get('attack_id')
    prompt = data.get('prompt')
    llm_provider = data.get('llm_provider', 'openai')  # 默认使用OpenAI
    llm_model = data.get('llm_model')  # 可选的具体模型
    
    # Get the attack
    attack = Attack.get_by_id(attack_id)
    if attack is None:
        return jsonify({"error": "Attack not found"}), 404
    
    algorithm_type = attack['algorithm_type']
    parameters = json.loads(attack['parameters']) if attack['parameters'] else {}
    
    try:
        # Generate jailbreak prompt
        jailbreak_prompt = apply_jailbreak(prompt, algorithm_type, **parameters)
        
        # Get response from LLM
        model_response = await llm_service.get_response(
            jailbreak_prompt,
            provider=llm_provider,
            model=llm_model
        )
        
        return jsonify({
            "original_prompt": prompt,
            "jailbreak_prompt": jailbreak_prompt,
            "model_response": model_response,
            "attack_name": attack['name'],
            "attack_id": attack_id,
            "llm_provider": llm_provider,
            "llm_model": llm_model
        })
    
    except Exception as e:
        return jsonify({
            "error": f"Failed to execute attack: {str(e)}"
        }), 500 