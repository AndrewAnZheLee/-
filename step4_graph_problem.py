import json
import os
import glob
import time
import google.generativeai as genai
from dotenv import load_dotenv

# === 設定區 ===
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)
model = genai.GenerativeModel('models/gemma-3-27b-it') 

def generate_chart_data(article_data):
    """
    專門負責產生「圖表數據」與「圖表題」的 AI 函數
    """
    title = article_data['meta']['title']
    content = article_data['content']
    
    print(f"📊 AI 正在為文章設計圖表：{title[:20]}...")

    prompt = f"""
    你是一位高中自然科老師。這是一篇科普文章的內容：
    
    ---
    {content[:1500]} 
    ---

    請根據文章內容，設計一個**「數據分析題」**。
    請判斷適合的圖表類型（折線圖、長條圖或散佈圖），並虛構一組符合科學原理的數據。

    請嚴格遵守以下 JSON 格式輸出：

    {{
        "chart_config": {{
            "type": "line", // 請填入 "line" (折線), "bar" (長條), 或 "scatter" (散佈)
            "title": "圖表標題",
            "x_label": "X軸名稱",
            "y_label": "Y軸名稱",
            "data_x": [數據...], 
            "data_y": [數據...]
        }},
        "question": "題目敘述...",
        "options": ["(A)...", "(B)...", "(C)...", "(D)..."],
        "correct_answer": "A",
        "explanation": "詳解"
    }}
    
    注意：
    1. 若是比較多個不同類別（如實驗組vs對照組），請用 "bar"。
    2. 若是觀察隨時間/溫度變化的趨勢，請用 "line"或"scatter"。
    3. 【長條圖 (bar)】：X 軸 (data_x) 必須是「類別名稱」(字串)。
       例如：data_x: ["對照組", "實驗組A", "實驗組B"], data_y: [10, 50, 85]
    4. 【折線圖 (line) / 散佈圖 (scatter)】：X 軸通常是「連續數值」(數字)。
       例如：data_x: [10, 20, 30, 40], data_y: [0.5, 0.8, 1.2, 1.5]
    5. 數據點數量建議 4~8 個。
    """

    try:
        response = model.generate_content(prompt, generation_config={"temperature": 0.2})
        text = response.text.strip()
        
        # 清洗 Markdown 標記 (防呆)
        if text.startswith("```"):
            text = text.replace("```json", "").replace("```", "").strip()
            
        return json.loads(text)
    except Exception as e:
        print(f"❌ 生成失敗: {e}")
        return None

def process_injection():
    # 掃描所有文章
    files = glob.glob("articles/**/*.json", recursive=True)
    
    count = 0
    for filepath in files:
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # 檢查：如果這篇文章已經有 'chart_quiz' 欄位，就跳過，避免重複浪費錢
            if "chart_quiz" in data:
                continue
                
            # 呼叫 AI 生成圖表資料
            chart_quiz_data = generate_chart_data(data)
            
            if chart_quiz_data:
                # 注入新資料！我們把這整包存進 'chart_quiz' 欄位
                data["chart_quiz"] = chart_quiz_data
                
                # 寫回檔案
                with open(filepath, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=4, ensure_ascii=False)
                
                print(f"✅ 成功注入圖表題：{filepath}")
                count += 1
                
                # 休息一下避免 API 限制
                time.sleep(2)
                
        except Exception as e:
            print(f"⚠️ 處理檔案出錯 {filepath}: {e}")
            continue

    if count == 0:
        print("📭 沒有需要處理的文章 (所有文章都已有圖表，或資料夾為空)。")
    else:
        print(f"🎉 完成！共為 {count} 篇文章加上了圖表題。")

if __name__ == "__main__":
    process_injection()