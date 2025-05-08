import os
import sys
from flask import Flask
from models.standard_qa import StandardQA
import openpyxl

def create_app():
    """创建一个Flask应用上下文以便访问数据库"""
    app = Flask(__name__)
    app.config['DATABASE'] = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database', 'jailbreak.db')
    return app

def import_qa_from_excel(excel_path, category=None):
    """从Excel文件导入问答对到数据库
    
    Args:
        excel_path: Excel文件路径
        category: 可选，问答对的类别
        
    Returns:
        导入的记录数
    """
    print(f"正在从 {excel_path} 导入数据...")
    
    try:
        # 读取Excel文件
        workbook = openpyxl.load_workbook(excel_path)
        sheet = workbook.active
        
        # 获取标题行
        headers = [cell.value for cell in sheet[1]]
        
        # 检查必要的列是否存在
        required_columns = ['prompt', 'standard response']
        col_indices = {}
        
        for col_name in required_columns:
            if col_name not in headers:
                print(f"错误: Excel文件必须包含列: {col_name}")
                return 0
            col_indices[col_name] = headers.index(col_name)
        
        # 准备数据
        qa_items = []
        
        # 从第二行开始读取数据（跳过标题行）
        for row in list(sheet.rows)[1:]:
            prompt = row[col_indices['prompt']].value
            standard_response = row[col_indices['standard response']].value
            
            # 确保值不为空
            if not prompt or not standard_response:
                continue
                
            qa_items.append((prompt, standard_response, category))
        
        # 批量插入数据库
        count = StandardQA.batch_create(qa_items)
        print(f"成功导入 {count} 条问答对")
        return count
        
    except Exception as e:
        print(f"导入过程中出错: {str(e)}")
        return 0

if __name__ == "__main__":
    """从命令行执行导入
    
    用法:
        python import_qa.py path/to/excel_file.xlsx [category]
    """
    if len(sys.argv) < 2:
        print("用法: python import_qa.py path/to/excel_file.xlsx [category]")
        sys.exit(1)
    
    excel_path = sys.argv[1]
    category = sys.argv[2] if len(sys.argv) > 2 else None
    
    app = create_app()
    with app.app_context():
        count = import_qa_from_excel(excel_path, category)
        
    sys.exit(0 if count > 0 else 1) 