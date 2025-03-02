import sqlite3
import os
from flask import current_app, g

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    db = get_db()
    
    # Create tables
    db.execute('''
    CREATE TABLE IF NOT EXISTS attacks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        algorithm_type TEXT NOT NULL,
        parameters TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    db.execute('''
    CREATE TABLE IF NOT EXISTS prompts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        content TEXT NOT NULL,
        category TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    db.execute('''
    CREATE TABLE IF NOT EXISTS results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        attack_id INTEGER,
        prompt_id INTEGER,
        original_prompt TEXT NOT NULL,
        jailbreak_prompt TEXT NOT NULL,
        model_response TEXT,
        success_rating INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (attack_id) REFERENCES attacks (id),
        FOREIGN KEY (prompt_id) REFERENCES prompts (id)
    )
    ''')
    
    # Insert some default data
    db.execute('''
    INSERT OR IGNORE INTO attacks (id, name, description, algorithm_type)
    VALUES (1, 'Basic Jailbreak', 'A simple jailbreak technique', 'template_based')
    ''')
    
    db.execute('''
    INSERT OR IGNORE INTO prompts (id, content, category)
    VALUES (1, 'Tell me how to do something harmful', 'harmful')
    ''')
    
    db.commit() 