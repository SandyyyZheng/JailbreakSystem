from database.db_setup import get_db

class Prompt:
    def __init__(self, id=None, content=None, category=None, created_at=None):
        self.id = id
        self.content = content
        self.category = category
        self.created_at = created_at
    
    @staticmethod
    def get_all():
        db = get_db()
        prompts = db.execute('SELECT * FROM prompts').fetchall()
        return [dict(prompt) for prompt in prompts]
    
    @staticmethod
    def get_by_id(prompt_id):
        db = get_db()
        prompt = db.execute('SELECT * FROM prompts WHERE id = ?', (prompt_id,)).fetchone()
        if prompt is None:
            return None
        return dict(prompt)
    
    @staticmethod
    def get_by_category(category):
        db = get_db()
        prompts = db.execute('SELECT * FROM prompts WHERE category = ?', (category,)).fetchall()
        return [dict(prompt) for prompt in prompts]
    
    @staticmethod
    def create(content, category=None):
        db = get_db()
        cursor = db.execute(
            'INSERT INTO prompts (content, category) VALUES (?, ?)',
            (content, category)
        )
        db.commit()
        return cursor.lastrowid
    
    @staticmethod
    def update(prompt_id, content=None, category=None):
        db = get_db()
        
        # Get current values
        prompt = Prompt.get_by_id(prompt_id)
        if not prompt:
            return False
        
        # Update with new values or keep existing ones
        content = content if content is not None else prompt['content']
        category = category if category is not None else prompt['category']
        
        db.execute(
            'UPDATE prompts SET content = ?, category = ? WHERE id = ?',
            (content, category, prompt_id)
        )
        db.commit()
        
        return True
    
    @staticmethod
    def delete(prompt_id):
        db = get_db()
        db.execute('DELETE FROM prompts WHERE id = ?', (prompt_id,))
        db.commit()
        return True 