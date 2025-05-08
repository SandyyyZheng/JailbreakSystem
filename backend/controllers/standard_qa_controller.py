from flask import Blueprint, request, jsonify
from models.standard_qa import StandardQA

standard_qa_bp = Blueprint('standard_qa', __name__)

@standard_qa_bp.route('/', methods=['GET'])
def get_standard_qa_items():
    """获取所有标准问答对或按类别筛选"""
    category = request.args.get('category')
    
    if category:
        qa_items = StandardQA.get_by_category(category)
    else:
        qa_items = StandardQA.get_all()
    
    return jsonify(qa_items)

@standard_qa_bp.route('/<int:qa_id>', methods=['GET'])
def get_standard_qa_item(qa_id):
    """获取单个标准问答对"""
    qa_item = StandardQA.get_by_id(qa_id)
    if qa_item is None:
        return jsonify({"error": "Standard QA item not found"}), 404
    return jsonify(qa_item)

@standard_qa_bp.route('/search', methods=['GET'])
def search_standard_qa():
    """根据提示词搜索标准问答对"""
    prompt = request.args.get('prompt')
    exact_match = request.args.get('exact_match', 'false').lower() == 'true'
    
    if not prompt:
        return jsonify({"error": "Prompt is required"}), 400
    
    if exact_match:
        qa_item = StandardQA.get_by_prompt(prompt, exact_match=True)
        if qa_item is None:
            return jsonify({"error": "No matching QA items found"}), 404
        return jsonify(qa_item)
    else:
        qa_items = StandardQA.get_by_prompt(prompt, exact_match=False)
        return jsonify(qa_items)

@standard_qa_bp.route('/', methods=['POST'])
def create_standard_qa():
    """创建新的标准问答对"""
    data = request.get_json()
    
    if not data or 'prompt' not in data or 'standard_response' not in data:
        return jsonify({"error": "Prompt and standard_response are required"}), 400
    
    prompt = data.get('prompt')
    standard_response = data.get('standard_response')
    category = data.get('category')
    
    # 检查是否已存在相同的prompt
    existing = StandardQA.get_by_prompt(prompt, exact_match=True)
    if existing:
        return jsonify({"error": "A QA item with this prompt already exists", "existing_id": existing['id']}), 409
    
    qa_id = StandardQA.create(prompt, standard_response, category)
    return jsonify({"id": qa_id, "message": "Standard QA item created successfully"}), 201

@standard_qa_bp.route('/<int:qa_id>', methods=['PUT'])
def update_standard_qa(qa_id):
    """更新标准问答对"""
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    prompt = data.get('prompt')
    standard_response = data.get('standard_response')
    category = data.get('category')
    
    success = StandardQA.update(qa_id, prompt, standard_response, category)
    
    if not success:
        return jsonify({"error": "Standard QA item not found"}), 404
    
    return jsonify({"message": "Standard QA item updated successfully"})

@standard_qa_bp.route('/<int:qa_id>', methods=['DELETE'])
def delete_standard_qa(qa_id):
    """删除标准问答对"""
    success = StandardQA.delete(qa_id)
    
    if not success:
        return jsonify({"error": "Standard QA item not found"}), 404
    
    return jsonify({"message": "Standard QA item deleted successfully"})

@standard_qa_bp.route('/batch-create', methods=['POST'])
def batch_create_standard_qa():
    """批量创建标准问答对"""
    data = request.get_json()
    
    if not data or 'items' not in data or not isinstance(data['items'], list):
        return jsonify({"error": "Items list is required"}), 400
    
    items = data.get('items')
    qa_items = []
    
    # 验证每个项目并准备批量插入
    for item in items:
        if not isinstance(item, dict) or 'prompt' not in item or 'standard_response' not in item:
            return jsonify({"error": "Each item must have prompt and standard_response"}), 400
        
        prompt = item.get('prompt')
        standard_response = item.get('standard_response')
        category = item.get('category')
        
        qa_items.append((prompt, standard_response, category))
    
    count = StandardQA.batch_create(qa_items)
    
    return jsonify({
        "message": f"Successfully created {count} standard QA items",
        "count": count
    }), 201 