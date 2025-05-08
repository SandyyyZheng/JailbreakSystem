import os
from flask import current_app
from models.standard_qa import StandardQA
import openpyxl

def init_qa_data():
    """初始化标准问答数据
    
    如果标准问答表为空，则从Q&A.xlsx导入数据
    """
    try:
        # 检查是否已有数据
        from database.db_setup import get_db
        db = get_db()
        count = db.execute('SELECT COUNT(*) as count FROM standard_qa').fetchone()['count']
        
        if count > 0:
            print(f"标准问答表已存在 {count} 条记录，跳过导入")
            return False
        
        # 如果没有数据，尝试导入
        excel_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'Q&A.xlsx')
        if not os.path.exists(excel_path):
            print(f"找不到文件: {excel_path}")
            return False
        
        print(f"正在从 {excel_path} 导入标准问答数据...")
        
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
                return False
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
                
            qa_items.append((prompt, standard_response, 'default'))
        
        # 批量插入数据库
        count = StandardQA.batch_create(qa_items)
        print(f"成功导入 {count} 条标准问答对")
        return True
        
    except Exception as e:
        print(f"初始化标准问答数据时出错: {str(e)}")
        return False 