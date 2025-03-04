import sqlite3
import os
from flask import current_app, g
import shutil

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

def is_first_run():
    """检查是否是首次运行"""
    db_path = current_app.config['DATABASE']
    return not os.path.exists(db_path)

def import_existing_data(source_db_path, target_db_path):
    """从现有数据库导入数据"""
    if os.path.exists(source_db_path):
        try:
            # 连接源数据库
            source_conn = sqlite3.connect(source_db_path)
            source_conn.row_factory = sqlite3.Row
            
            # 确保目标目录存在
            os.makedirs(os.path.dirname(target_db_path), exist_ok=True)
            
            # 连接目标数据库
            target_conn = sqlite3.connect(target_db_path)
            target_conn.row_factory = sqlite3.Row
            
            # 获取所有表的数据
            tables = ['attacks', 'prompts', 'results']
            
            # 创建表结构
            target_conn.executescript('''
                CREATE TABLE IF NOT EXISTS attacks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    description TEXT,
                    algorithm_type TEXT NOT NULL,
                    parameters TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE TABLE IF NOT EXISTS prompts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content TEXT NOT NULL,
                    category TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
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
                );
            ''')
            
            # 导入每个表的数据
            for table in tables:
                # 获取源数据
                rows = source_conn.execute(f'SELECT * FROM {table}').fetchall()
                if rows:
                    # 获取列名
                    columns = [description[0] for description in source_conn.execute(f'SELECT * FROM {table}').description]
                    # 构建插入语句
                    placeholders = ','.join(['?' for _ in columns])
                    column_names = ','.join(columns)
                    insert_sql = f'INSERT OR REPLACE INTO {table} ({column_names}) VALUES ({placeholders})'
                    
                    # 插入数据
                    for row in rows:
                        target_conn.execute(insert_sql, tuple(row))
            
            # 提交更改
            target_conn.commit()
            
            # 关闭连接
            source_conn.close()
            target_conn.close()
            
            return True
            
        except Exception as e:
            print(f"Error importing database: {str(e)}")
            # 如果发生错误，删除可能创建的不完整目标数据库
            if os.path.exists(target_db_path):
                os.remove(target_db_path)
            return False
    return False

def init_db():
    db_path = current_app.config['DATABASE']
    
    # 检查是否是首次运行
    if is_first_run():
        # 尝试从项目目录中导入现有的数据库
        source_db = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'jailbreak.db')
        if import_existing_data(source_db, db_path):
            print(f"Successfully imported existing database from {source_db}")
            return
    
    # 如果没有找到现有数据库或不是首次运行，创建新的数据库结构
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