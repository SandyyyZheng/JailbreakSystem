from flask import Blueprint, request, jsonify
from models.attack import Attack
from utils.jailbreak_algorithms import apply_jailbreak
import json

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
def execute_attack():
    """
    Execute a jailbreak attack on a prompt
    """
    data = request.get_json()
    
    if not data or 'attack_id' not in data or 'prompt' not in data:
        return jsonify({"error": "Attack ID and prompt are required"}), 400
    
    attack_id = data.get('attack_id')
    prompt = data.get('prompt')
    
    # Get the attack
    attack = Attack.get_by_id(attack_id)
    if attack is None:
        return jsonify({"error": "Attack not found"}), 404
    
    # TODO: This is where you'll implement your black-box attack algorithm
    # The implementation will depend on the algorithm_type
    
    algorithm_type = attack['algorithm_type']
    parameters = json.loads(attack['parameters']) if attack['parameters'] else {}

    # Call the function in jailbreak_algorithms.py
    jailbreak_prompt = apply_jailbreak(prompt, algorithm_type, **parameters)
    
    return jsonify({
        "original_prompt": prompt,
        "jailbreak_prompt": jailbreak_prompt,
        "attack_name": attack['name'],
        "attack_id": attack_id
    }) 