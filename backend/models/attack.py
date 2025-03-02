import json
from database.db_setup import get_db

class Attack:
    def __init__(self, id=None, name=None, description=None, algorithm_type=None, parameters=None, created_at=None):
        self.id = id
        self.name = name
        self.description = description
        self.algorithm_type = algorithm_type
        self.parameters = parameters
        self.created_at = created_at
    
    @staticmethod
    def get_all():
        db = get_db()
        attacks = db.execute('SELECT * FROM attacks').fetchall()
        return [dict(attack) for attack in attacks]
    
    @staticmethod
    def get_by_id(attack_id):
        db = get_db()
        attack = db.execute('SELECT * FROM attacks WHERE id = ?', (attack_id,)).fetchone()
        if attack is None:
            return None
        return dict(attack)
    
    @staticmethod
    def create(name, description, algorithm_type, parameters=None):
        db = get_db()
        params_json = json.dumps(parameters) if parameters else None
        
        cursor = db.execute(
            'INSERT INTO attacks (name, description, algorithm_type, parameters) VALUES (?, ?, ?, ?)',
            (name, description, algorithm_type, params_json)
        )
        db.commit()
        
        return cursor.lastrowid
    
    @staticmethod
    def update(attack_id, name=None, description=None, algorithm_type=None, parameters=None):
        db = get_db()
        
        # Get current values
        attack = Attack.get_by_id(attack_id)
        if not attack:
            return False
        
        # Update with new values or keep existing ones
        name = name if name is not None else attack['name']
        description = description if description is not None else attack['description']
        algorithm_type = algorithm_type if algorithm_type is not None else attack['algorithm_type']
        
        # Handle parameters (JSON)
        if parameters is not None:
            params_json = json.dumps(parameters)
        else:
            params_json = attack['parameters']
        
        db.execute(
            'UPDATE attacks SET name = ?, description = ?, algorithm_type = ?, parameters = ? WHERE id = ?',
            (name, description, algorithm_type, params_json, attack_id)
        )
        db.commit()
        
        return True
    
    @staticmethod
    def delete(attack_id):
        db = get_db()
        db.execute('DELETE FROM attacks WHERE id = ?', (attack_id,))
        db.commit()
        return True 