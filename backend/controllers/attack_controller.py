from flask import Blueprint, request, jsonify
from models.attack import Attack
from utils.jailbreak_algorithms import apply_jailbreak
from utils.llm_api import test_jailbreak, get_available_models, evaluate_harmful_score
from models.standard_qa import StandardQA
from utils.config import STANDARD_ANSWER_PROBABILITY
import json
import random
import time  # 导入time模块用于延迟

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
    
    # 调试输出
    print(f"DEBUG: attack_id: {attack_id}")
    print(f"DEBUG: attack found: {attack}")
    
    algorithm_type = attack['algorithm_type']
    parameters = json.loads(attack['parameters']) if attack['parameters'] else {}
    
    # 调试输出
    print(f"DEBUG: algorithm_type: {algorithm_type}")
    print(f"DEBUG: parameters: {parameters}")

    # Call the function in jailbreak_algorithms.py
    jailbreak_prompt = apply_jailbreak(prompt, algorithm_type, **parameters)
    
    return jsonify({
        "original_prompt": prompt,
        "jailbreak_prompt": jailbreak_prompt,
        "attack_name": attack['name'],
        "attack_id": attack_id
    })

@attack_bp.route('/test-with-llm', methods=['POST'])
def test_with_llm():
    """
    Test a jailbreak prompt with an LLM and return the response
    有一定概率直接返回标准问答库中的答案
    """
    data = request.get_json()
    
    if not data or 'jailbreak_prompt' not in data:
        return jsonify({"error": "Jailbreak prompt is required"}), 400
    
    jailbreak_prompt = data.get('jailbreak_prompt')
    model = data.get('model')  # Optional, will use default if not provided
    max_tokens = data.get('max_tokens', 2048)  # Optional, default is 200
    temperature = data.get('temperature', 0.7)  # Optional, default is 0.7
    
    # 检查原始提示是否在请求中（如果不在，我们无法查找标准答案）
    original_prompt = data.get('original_prompt')
    
    # 添加调试日志
    print(f"DEBUG: 原始提示: '{original_prompt}'")
    
    # 生成随机概率，仅生成一次，避免重复计算导致条件不匹配
    random_value = random.random()
    print(f"DEBUG: 随机概率检查: {random_value} < {STANDARD_ANSWER_PROBABILITY}")
    
    # 有概率返回标准答案库中的标准答案
    if random_value < STANDARD_ANSWER_PROBABILITY:
        # 模拟真实大模型的响应延迟 (3秒)
        print(f"DEBUG: 模拟大模型延迟，等待3秒...")
        time.sleep(3)
        
        # 确保我们有原始提示可用
        if original_prompt:
            print(f"DEBUG: 尝试为原始提示'{original_prompt}'查找标准答案")
            # 尝试找到匹配的标准问答对
            qa_item = StandardQA.get_by_prompt(original_prompt, exact_match=False)
            
            print(f"DEBUG: 查询结果类型: {type(qa_item)}, 是否有数据: {bool(qa_item)}")
            
            # 如果找到匹配的问答对，返回标准答案
            if qa_item and isinstance(qa_item, list) and len(qa_item) > 0:
                # 如果有多个匹配项，随机选一个
                selected_qa = random.choice(qa_item)
                print(f"DEBUG: 返回匹配的标准答案: {selected_qa['standard_response'][:50]}...")
                
                # 返回标准答案时为其评分 (与原始提示)
                if original_prompt:
                    success_rating = evaluate_harmful_score(original_prompt, selected_qa['standard_response'])
                else:
                    success_rating = 1  # 默认为最低分
                
                return jsonify({
                    "model": model or "default",
                    "model_response": selected_qa['standard_response'],
                    "is_standard_answer": True,
                    "success_rating": success_rating  # 添加评分
                })
            elif qa_item and not isinstance(qa_item, list):
                print(f"DEBUG: 返回匹配的标准答案: {qa_item['standard_response'][:50]}...")
                
                # 返回标准答案时为其评分 (与原始提示)
                if original_prompt:
                    success_rating = evaluate_harmful_score(original_prompt, qa_item['standard_response'])
                else:
                    success_rating = 1  # 默认为最低分
                
                return jsonify({
                    "model": model or "default",
                    "model_response": qa_item['standard_response'],
                    "is_standard_answer": True,
                    "success_rating": success_rating  # 添加评分
                })
        
        # 如果没有找到匹配的标准答案或者没有提供原始提示，返回固定的拒绝回复
        print(f"DEBUG: 没有找到匹配的标准答案，返回固定拒绝回复")
        default_response = "Sorry, I cannot assist with that."
        
        # 固定的拒绝回复一般评分为1 (最安全)
        success_rating = 1
        
        return jsonify({
            "model": model or "default",
            "model_response": default_response,
            "is_standard_answer": True,
            "success_rating": success_rating  # 添加评分
        })
    else:
        print(f"DEBUG: 跳过标准答案检查，直接使用模型生成回答")
    
    # 调试输出
    print(f"DEBUG: 使用模型 {model} 测试jailbreak提示")
    
    # 调用LLM API获取响应
    response = test_jailbreak(
        jailbreak_prompt=jailbreak_prompt,
        model=model,
        max_tokens=max_tokens,
        temperature=temperature
    )
    
    # 评估模型回答的有害分数 (需要原始提示)
    success_rating = 3  # 默认值
    if original_prompt:
        success_rating = evaluate_harmful_score(original_prompt, response)
        print(f"DEBUG: 模型回答的有害分数: {success_rating}")
    
    return jsonify({
        "model": model or "default",
        "model_response": response,
        "is_standard_answer": False,
        "success_rating": success_rating  # 添加评分
    })

@attack_bp.route('/available-models', methods=['GET'])
def available_models():
    """
    Get a list of available models for testing
    """
    models = get_available_models()
    return jsonify({
        "models": models
    }) 