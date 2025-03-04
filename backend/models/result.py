from database.db_setup import get_db

class Result:
    def __init__(self, id=None, attack_id=None, prompt_id=None, original_prompt=None, 
                 jailbreak_prompt=None, model_response=None, success_rating=None, created_at=None):
        self.id = id
        self.attack_id = attack_id
        self.prompt_id = prompt_id
        self.original_prompt = original_prompt
        self.jailbreak_prompt = jailbreak_prompt
        self.model_response = model_response
        self.success_rating = success_rating
        self.created_at = created_at
    
    @staticmethod
    def get_all():
        db = get_db()
        results = db.execute('''
            SELECT r.*, a.name as attack_name, p.content as prompt_content 
            FROM results r
            LEFT JOIN attacks a ON r.attack_id = a.id
            LEFT JOIN prompts p ON r.prompt_id = p.id
        ''').fetchall()
        return [dict(result) for result in results]
    
    @staticmethod
    def get_by_id(result_id):
        db = get_db()
        result = db.execute('''
            SELECT r.*, a.name as attack_name, p.content as prompt_content 
            FROM results r
            LEFT JOIN attacks a ON r.attack_id = a.id
            LEFT JOIN prompts p ON r.prompt_id = p.id
            WHERE r.id = ?
        ''', (result_id,)).fetchone()
        if result is None:
            return None
        return dict(result)
    
    @staticmethod
    def get_by_attack(attack_id):
        db = get_db()
        results = db.execute('''
            SELECT r.*, a.name as attack_name, p.content as prompt_content 
            FROM results r
            LEFT JOIN attacks a ON r.attack_id = a.id
            LEFT JOIN prompts p ON r.prompt_id = p.id
            WHERE r.attack_id = ?
        ''', (attack_id,)).fetchall()
        return [dict(result) for result in results]
    
    @staticmethod
    def create(attack_id, prompt_id, original_prompt, jailbreak_prompt, model_response=None, success_rating=None):
        db = get_db()
        cursor = db.execute(
            '''INSERT INTO results 
               (attack_id, prompt_id, original_prompt, jailbreak_prompt, model_response, success_rating) 
               VALUES (?, ?, ?, ?, ?, ?)''',
            (attack_id, prompt_id, original_prompt, jailbreak_prompt, model_response, success_rating)
        )
        db.commit()
        return cursor.lastrowid
    
    @staticmethod
    def update(result_id, model_response=None, success_rating=None):
        db = get_db()
        
        # Get current values
        result = Result.get_by_id(result_id)
        if not result:
            return False
        
        # 打印日志以便调试
        print(f"Current result: {result}")
        print(f"Updating with model_response: {model_response}, success_rating: {success_rating}")
        
        # Update with new values or keep existing ones
        model_response = model_response if model_response is not None else result['model_response']
        success_rating = success_rating if success_rating is not None else result['success_rating']
        
        # 确保success_rating是整数或浮点数，且在1-5的范围内
        if success_rating is not None:
            try:
                success_rating = float(success_rating)
                # 限制在1-5的范围内
                success_rating = min(max(success_rating, 1), 5)
            except (ValueError, TypeError):
                print(f"Warning: Invalid success_rating value: {success_rating}")
                success_rating = result['success_rating']
        
        db.execute(
            'UPDATE results SET model_response = ?, success_rating = ? WHERE id = ?',
            (model_response, success_rating, result_id)
        )
        db.commit()
        
        # 打印更新后的结果
        updated_result = Result.get_by_id(result_id)
        print(f"Updated result: {updated_result}")
        
        return True
    
    @staticmethod
    def delete(result_id):
        db = get_db()
        db.execute('DELETE FROM results WHERE id = ?', (result_id,))
        db.commit()
        return True 