from database.db_setup import get_db

class StandardQA:
    def __init__(self, id=None, prompt=None, standard_response=None, category=None, created_at=None):
        self.id = id
        self.prompt = prompt
        self.standard_response = standard_response
        self.category = category
        self.created_at = created_at
    
    @staticmethod
    def get_all():
        db = get_db()
        qa_items = db.execute('SELECT * FROM standard_qa ORDER BY id').fetchall()
        return [dict(item) for item in qa_items]
    
    @staticmethod
    def get_by_id(qa_id):
        db = get_db()
        qa_item = db.execute('SELECT * FROM standard_qa WHERE id = ?', (qa_id,)).fetchone()
        if qa_item is None:
            return None
        return dict(qa_item)
    
    @staticmethod
    def get_by_prompt(prompt, exact_match=True):
        db = get_db()
        print(f"DEBUG StandardQA: 尝试查找提示: '{prompt}', 精确匹配={exact_match}")
        
        if exact_match:
            qa_item = db.execute('SELECT * FROM standard_qa WHERE prompt = ?', (prompt,)).fetchone()
            result = dict(qa_item) if qa_item else None
            print(f"DEBUG StandardQA: 精确匹配结果: {result}")
            return result
        else:
            # 使用更宽松的匹配逻辑
            # 1. 首先尝试包含关系匹配
            search_term = f"%{prompt}%"
            qa_items = db.execute('SELECT * FROM standard_qa WHERE prompt LIKE ?', (search_term,)).fetchall()
            
            # 2. 如果没有找到结果，尝试反向匹配（原始提示包含标准问题）
            if not qa_items:
                print(f"DEBUG StandardQA: 没有找到包含关系匹配，尝试反向匹配")
                # 获取所有问题，然后在Python中检查哪些标准问题包含在原始提示中
                all_qa_items = db.execute('SELECT * FROM standard_qa').fetchall()
                matching_items = []
                
                for item in all_qa_items:
                    if item['prompt'] and item['prompt'] in prompt:
                        matching_items.append(item)
                
                if matching_items:
                    result = [dict(item) for item in matching_items]
                    print(f"DEBUG StandardQA: 反向匹配找到 {len(result)} 个结果")
                    return result
            
            if qa_items:
                result = [dict(item) for item in qa_items]
                print(f"DEBUG StandardQA: 包含关系匹配找到 {len(result)} 个结果")
                return result
            
            print(f"DEBUG StandardQA: 未找到任何匹配结果")
            return []
    
    @staticmethod
    def get_by_category(category):
        db = get_db()
        qa_items = db.execute('SELECT * FROM standard_qa WHERE category = ?', (category,)).fetchall()
        return [dict(item) for item in qa_items]
    
    @staticmethod
    def create(prompt, standard_response, category=None):
        db = get_db()
        cursor = db.execute(
            'INSERT INTO standard_qa (prompt, standard_response, category) VALUES (?, ?, ?)',
            (prompt, standard_response, category)
        )
        db.commit()
        return cursor.lastrowid
    
    @staticmethod
    def update(qa_id, prompt=None, standard_response=None, category=None):
        db = get_db()
        
        # 获取当前记录
        qa_item = StandardQA.get_by_id(qa_id)
        if not qa_item:
            return False
        
        # 更新值
        prompt = prompt if prompt is not None else qa_item['prompt']
        standard_response = standard_response if standard_response is not None else qa_item['standard_response']
        category = category if category is not None else qa_item['category']
        
        db.execute(
            'UPDATE standard_qa SET prompt = ?, standard_response = ?, category = ? WHERE id = ?',
            (prompt, standard_response, category, qa_id)
        )
        db.commit()
        return True
    
    @staticmethod
    def delete(qa_id):
        db = get_db()
        db.execute('DELETE FROM standard_qa WHERE id = ?', (qa_id,))
        db.commit()
        return True
    
    @staticmethod
    def batch_create(qa_items):
        """批量创建标准问答对
        
        Args:
            qa_items: 包含 (prompt, standard_response, category) 元组的列表
        
        Returns:
            创建的记录数量
        """
        db = get_db()
        count = 0
        for prompt, standard_response, category in qa_items:
            db.execute(
                'INSERT INTO standard_qa (prompt, standard_response, category) VALUES (?, ?, ?)',
                (prompt, standard_response, category)
            )
            count += 1
        db.commit()
        return count 