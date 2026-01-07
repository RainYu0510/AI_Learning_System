from fastapi import FastAPI, HTTPException    # 第一行：導入 Web 框架 [cite: 59]
from pydantic import BaseModel                # 第二行：用於定義資料驗證模型 [cite: 59]
import pymysql                                # 第三行：MySQL 資料庫驅動程式 [cite: 56]
from fastapi.middleware.cors import CORSMiddleware
import random

app = FastAPI()

# 允許前端網頁進行跨網域存取 (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 資料庫連線配置 (對應資料庫系統解決方案 [cite: 49, 56])
def get_db():
    return pymysql.connect(
        host='localhost', 
        user='root', 
        password='', # 請填入您的 MySQL 密碼
        database='adaptive_learning_db', 
        cursorclass=pymysql.cursors.DictCursor
    )

# 定義前端傳入的資料格式
class Submission(BaseModel):
    user_id: int
    question_id: int
    answer: str



@app.get("/generate-question")
async def generate_question():
    db = get_db()
    cursor = db.cursor()

    num1 = random.randint(-10, 10)
    num2 = random.randint(-10, 10)

    ops = ['+', '-', '*', '/']
    op = random.choice(ops)

    # 避免除以 0
    if op == '/':
        while num2 == 0:
            num2 = random.randint(-10, 10)
        correct = num1 / num2
        correct_answer = str(round(correct, 2))  # 取小數兩位
    elif op == '+':
        correct_answer = str(num1 + num2)
    elif op == '-':
        correct_answer = str(num1 - num2)
    else:  # '*'
        correct_answer = str(num1 * num2)

    content = f"計算 ({num1}) {op} ({num2}) = ?"

    new_id = random.randint(100, 9999)

    sql = """
        INSERT INTO Questions
        (QuestionID, Content, Subject, CorrectAnswer, Tags)
        VALUES (%s, %s, %s, %s, %s)
    """
    cursor.execute(sql, (
        new_id,
        content,
        'Math',
        correct_answer,
        f'AI自動出題-{op}'
    ))
    db.commit()

    return {
        "question_id": new_id,
        "content": content
    }


@app.post("/submit")
async def submit_answer(data: Submission):
    db = get_db()
    try:
        with db.cursor() as cursor:
            # 1. 查詢題目資訊與標籤 [cite: 62]
            cursor.execute("SELECT CorrectAnswer, Tags FROM Questions WHERE QuestionID=%s", (data.question_id,))
            q = cursor.fetchone()
            
            is_correct = float(data.answer) == float(q['CorrectAnswer'])
            
            # 2. 存入作答紀錄 (Answers 表) [cite: 62]
            cursor.execute("INSERT INTO Answers (UserID, QuestionID, UserAnswer, IsCorrect) VALUES (%s, %s, %s, %s)", 
                           (data.user_id, data.question_id, data.answer, is_correct))
            
            # 3. AI 錯誤分析邏輯 (解決「不了解為何而錯」的痛點 [cite: 9, 31, 32])
            analysis = None
            if not is_correct:
                error_type = "邏輯運算錯誤"
                suggestion = f"AI 分析建議：針對標籤「{q['Tags']}」進行複習。正確答案為 {q['CorrectAnswer']}。"
                
                # 存入 AI_Analysis 表 [cite: 62]
                cursor.execute("INSERT INTO AI_Analysis (UserID, QuestionID, ErrorType, Suggestion) VALUES (%s, %s, %s, %s)",
                               (data.user_id, data.question_id, error_type, suggestion))
                analysis = {"type": error_type, "msg": suggestion}
            
            db.commit()
            return {"correct": is_correct, "ai_feedback": analysis}
    finally:
        db.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)