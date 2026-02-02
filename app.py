import streamlit as st
import json
import os
import glob
import pandas as pd
import plotly.graph_objects as go
# === 1. 頁面基礎設定 ===
st.set_page_config(
    page_title="分科測驗素養練習",
    page_icon="🧬",
    layout="wide", # 使用寬螢幕模式
    initial_sidebar_state="expanded"
)

# === 2. 核心邏輯：讀取資料庫 ===
def load_articles():
    base_dir = "articles"
    if not os.path.exists(base_dir):
        return []

    # 搜尋所有子資料夾中的 JSON
    # 結構: articles/physics/xxx.json
    files = glob.glob(f"{base_dir}/**/*.json", recursive=True)
    
    articles = []
    for filepath in files:
        if os.path.isfile(filepath):
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    
                    # 補上一些前端需要的屬性
                    # 從路徑判斷科目 (windows/linux 路徑分隔符號處理)
                    folder_name = os.path.basename(os.path.dirname(filepath))
                    data['subject_category'] = folder_name
                    data['filepath'] = filepath
                    
                    articles.append(data)
            except Exception as e:
                print(f"Error loading {filepath}: {e}")
                continue
    
    # 按照 id (通常是日期開頭) 倒序排列，新的在前面
    articles.sort(key=lambda x: x.get('id', ''), reverse=True)
    return articles

def get_subject_emoji(subject):
    if "physics" in subject: return "⚛️"
    if "chemistry" in subject: return "⚗️"
    if "biology" in subject: return "🧬"
    return "📄"

# === 3. 介面佈局 ===

# 載入資料
all_articles = load_articles()

# 側邊欄：標題與篩選
with st.sidebar:
    st.title("🔬 科普日報")
    st.markdown("針對**分科測驗**素養題設計的閱讀網站")
    st.divider()

    # 科目篩選器
    subject_filter = st.radio(
        "選擇科目資料夾：",
        ["全部顯示", "physics (物理)", "chemistry (化學)", "biology (生物)"],
        index=0
    )
    
    st.info(f"目前資料庫共有 {len(all_articles)} 篇文章")
    
# 重新整理按鈕
    if st.button("🔄 重新載入資料庫"):
        st.rerun()

    # === ✨ 新增：使用條款與免責聲明 ===
    st.divider() # 加一條分隔線
    
    with st.expander("ℹ️ 使用條款與免責聲明"):
        st.markdown("""
        ### 1. AI 生成內容聲明
        本應用程式之文章、試題與圖表數據皆由 **人工智慧 (AI)** 根據學術論文摘要自動生成。使用模型包括 Gemini 2.0 2.5 3.0 與 Gemma 3。
        * 內容旨在輔助**高中分科測驗**備考與科普新知擴充。
        * AI 可能產生「幻覺」或數據誤差，**若內容與高中教科書有出入，請以教育部審定之教科書為準**。
        
        ### 2. 非專業建議
        本平台內容僅供學術討論與考試訓練：
        * **生物/醫學類文章**：僅供生物學理探討，**絕不可作為醫療診斷、用藥或治療依據**。身體不適請諮詢專業醫師。
        * **物理/化學類文章**：實驗數據多為模擬生成，進行實作時請務必遵循實驗室安全規範。

        ### 3. 資料來源與版權
        * 原始論文來源為公開資料庫 [arXiv](https://arxiv.org/) 與 [PubMed](https://pubmed.ncbi.nlm.nih.gov/)。
        * 本 App 僅進行轉譯、改寫與教學應用，原始論文版權歸原作者所有。
        
        ### 4. 隱私權
        * 本程式目前於本地端環境運行，**不會**收集使用者的個人瀏覽紀錄或個資。
        ### 5. 疑難排解
        * 有任何問題可以向開發者**李安哲**詢問。
        """)
        st.caption("© 分科測驗素養科普 ")
        st.caption("台南一中 李安哲 ")

# 主畫面內容邏輯
if not all_articles:
    st.warning("📭 資料庫是空的！")
    st.markdown("""
    ### 快速啟動指南：
    1. 執行 `python step2_fetch_papers.py` 抓取論文。
    2. 執行 `python step3_ai_processor.py` 生成文章。
    3. 重新整理此頁面。
    """)
else:
    # 1. 根據側邊欄篩選資料
    if subject_filter == "全部顯示":
        filtered_articles = all_articles
    else:
        # 取出括號前的英文單字來比對 (例如 "physics")
        target_sub = subject_filter.split(" ")[0]
        filtered_articles = [a for a in all_articles if a['subject_category'] == target_sub]

    if not filtered_articles:
        st.info("此分類目前沒有文章。趕快去抓幾篇吧！")
    else:
        # 2. 雙欄佈局：左邊選單，右邊閱讀
        col_menu, col_content = st.columns([1, 2.5])

        with col_menu:
            st.subheader("📚 文章列表")
            # 製作選單項目標題
            options = {
                index: f"{get_subject_emoji(a['subject_category'])} {a['meta']['published']} | {a['meta']['title']}"
                for index, a in enumerate(filtered_articles)
            }
            
            # 使用 radio button 當作導航列
            selected_index = st.radio(
                "請點擊閱讀：",
                options=options.keys(),
                format_func=lambda x: options[x],
                label_visibility="collapsed"
            )

        with col_content:
            article = filtered_articles[selected_index]
            meta = article['meta']
            content = article['content']
            
            # === 1. 顯示文章 header ===
            st.markdown(f"### {meta.get('title', '無標題')}")
            c1, c2, c3 = st.columns(3)
            with c1: st.caption(f"**科目：** {article['subject_category'].upper()}")
            with c2: st.caption(f"**日期：** {meta.get('published', '未知')}")
            with c3: st.caption(f"**來源：** [{meta.get('source')}]({meta.get('url', '#')})")
            st.divider()
            
           # === 2. 智慧解析：分離文章與題目 (增強版) ===
            
            article_text = content
            json_text = None
            
            # 策略 A：標準模式 (找特定標籤)
            marker = "===QUIZ_JSON==="
            if marker in content:
                parts = content.split(marker)
                article_text = parts[0]
                json_text = parts[1]
            
            # 策略 B：備用模式 (如果 AI 忘記加標籤，但有加分隔線)
            elif "\n---" in content:
                # rsplit 代表從右邊(後面)開始切，切 1 刀
                # 這樣可以找到文章最後面那一段
                parts = content.rsplit("\n---", 1)
                
                # 檢查切出來的後半段像不像 JSON (有大括號)
                if len(parts) > 1 and "{" in parts[1] and "}" in parts[1]:
                    candidate_json = parts[1].strip()
                    # 簡單檢查一下開頭是不是 {
                    if candidate_json.startswith("{") or candidate_json.startswith("```"):
                        article_text = parts[0]
                        json_text = candidate_json

            # 如果成功抓到 JSON 文字，就開始解析
            if json_text:
                # 顯示科普文章本體
                st.markdown(article_text)
                
                # === 3. 互動式測驗區 ===
            st.divider()
            st.subheader("📝 隨堂測驗")

            # -------------------------------------------------------
            # 第一部分：基礎觀念題 (來自 Step 3 的文字題)
            # -------------------------------------------------------
            text_quiz_data = None
            
            # 嘗試解析文章內的 JSON
            if "===QUIZ_JSON===" in content:
                 try:
                     parts = content.split("===QUIZ_JSON===")
                     json_text = parts[1].strip()
                     if json_text.startswith("```"):
                         json_text = json_text.replace("```json", "").replace("```", "").strip()
                     text_quiz_data = json.loads(json_text)
                 except:
                     pass
            elif "\n---" in content: # 備用解析策略
                 try:
                     parts = content.rsplit("\n---", 1)
                     if len(parts) > 1 and "{" in parts[1]:
                         json_text = parts[1].strip()
                         if json_text.startswith("```"):
                             json_text = json_text.replace("```json", "").replace("```", "").strip()
                         text_quiz_data = json.loads(json_text)
                 except:
                     pass

            if text_quiz_data:
                st.markdown("#### 🔹 第一題：基礎觀念")
                st.write(f"**題目：** {text_quiz_data['question']}")
                
                # 注意 key 必須加上 _text 後綴，避免跟下面的圖表題衝突
                user_choice_text = st.radio(
                    "請選擇答案：",
                    text_quiz_data['options'],
                    key=f"radio_text_{article['id']}", 
                    index=None
                )
                
                if st.button("送出答案 (基礎題)", key=f"btn_text_{article['id']}"):
                    if user_choice_text:
                        ans = text_quiz_data['correct_answer'].upper()
                        if f"({ans})" in user_choice_text:
                            st.success(f"🎉 答對了！")
                            st.info(f"詳解：{text_quiz_data['explanation']}")
                        else:
                            st.error(f"❌ 答錯了！正確答案是 {ans}")
                            st.info(f"詳解：{text_quiz_data['explanation']}")
                    else:
                        st.warning("請先作答！")
            else:
                st.info("本篇文章無基礎文字題。")

            # -------------------------------------------------------
            # 第二部分：進階圖表題 (來自 Step 4 的注入資料)
            # -------------------------------------------------------
            if "chart_quiz" in article:
                st.markdown("---")
                st.markdown("#### 📊 第二題：數據分析")
                
                chart_data = article["chart_quiz"]
                
                if "chart_config" in chart_data:
                    c = chart_data["chart_config"]
                    st.caption(f"圖表：{c.get('title', '數據分析')}")
                    
                    try:
                        # 1. 建立 Figure 物件
                        fig = go.Figure()
                        
                        # 2. 判斷圖表類型 (Line, Bar, Scatter)
                        chart_type = c.get("type", "line").lower()
                        
                        # 定義科學風格的顏色 (經典藍)
                        science_color = "#1da3b4" 

                        # === 針對不同類型加入不同的 Trace ===
                        if chart_type == "bar":
                            # 長條圖
                            fig.add_trace(go.Bar(
                                x=c['data_x'],
                                y=c['data_y'],
                                name='Data',
                                marker_color=science_color,
                                # 如果是長條圖，可以設定寬度讓它不要太擠
                                # width=0.5 
                            ))
                        
                        elif chart_type == "scatter":
                            # 散佈圖 (只有點，沒有線)
                            fig.add_trace(go.Scatter(
                                x=c['data_x'],
                                y=c['data_y'],
                                mode='markers',
                                name='Data',
                                marker=dict(size=10, color=science_color)
                            ))
                            
                        else:
                            # 預設：折線圖 (線 + 點)
                            fig.add_trace(go.Scatter(
                                x=c['data_x'], 
                                y=c['data_y'],
                                mode='lines+markers',
                                name='Data',
                                line=dict(color=science_color, width=4),
                                marker=dict(size=12)
                            ))

                        # 3. === 關鍵樣式設定 (科學期刊風格 + 大字體黑粗版) ===
                        fig.update_layout(
                            template="plotly_white",
                            
                            # --- 1. 主標題設定 ---
                            title=dict(
                                text=c.get('title', ''),
                                x=0.5,              # ✅ 強制置中 (原本可能是自動或靠右)
                                y=0.9,              # 稍微留點上方邊距
                                xanchor='center',
                                yanchor='top',
                                font=dict(
                                    family="Microsoft JhengHei, Arial Black, sans-serif", # 優先用正黑體或粗體
                                    size=24,        # ✅ 標題字體加大
                                    color="black"   # ✅ 純黑
                                )
                            ),
                            
                            font=dict(family="Arial", size=14, color="black"),
                            margin=dict(l=80, r=40, t=80, b=80), # 邊距加大一點以免字太大切到
                            
                            # --- 2. X 軸設定 ---
                            xaxis=dict(
                                title=dict(
                                    text=c.get('x_label', 'X-Axis'),
                                    font=dict(size=20, family="Arial Black", color="black") # ✅ 軸標題加大加粗
                                ),
                                showgrid=False,
                                showline=True,
                                linewidth=3,          # ✅ 框線更粗 (2 -> 3)
                                linecolor='black',
                                ticks='inside',
                                tickwidth=3,          # ✅ 刻度更粗
                                tickcolor='black',
                                mirror=True,
                                # 數值標籤設定
                                tickfont=dict(
                                    size=16,          # ✅ 軸數值加大
                                    family="Arial Black", 
                                    color="black"
                                )
                            ),
                            
                            # --- 3. Y 軸設定 ---
                            yaxis=dict(
                                title=dict(
                                    text=c.get('y_label', 'Y-Axis'),
                                    font=dict(size=20, family="Arial Black", color="black") # ✅ 軸標題加大加粗
                                ),
                                showgrid=False,
                                showline=True,
                                linewidth=3,          # ✅ 框線更粗
                                linecolor='black',
                                ticks='inside',
                                tickwidth=3,
                                tickcolor='black',
                                mirror=True,
                                # 數值標籤設定
                                tickfont=dict(
                                    size=16,          # ✅ 軸數值加大
                                    family="Arial Black", 
                                    color="black"
                                )
                            ),
                            showlegend=False
                        )

                        # 4. 顯示
                        st.plotly_chart(fig, use_container_width=True)
                            
                    except Exception as e:
                        st.error(f"圖表繪製失敗: {e}")
                # 2. 顯示題目
                st.write(f"**題目：** {chart_data['question']}")
                
                # 注意 key 必須加上 _chart 後綴
                user_choice_chart = st.radio(
                    "請選擇答案：",
                    chart_data['options'],
                    key=f"radio_chart_{article['id']}",
                    index=None
                )
                
                if st.button("送出答案 (圖表題)", key=f"btn_chart_{article['id']}"):
                    if user_choice_chart:
                        ans = chart_data['correct_answer'].upper()
                        if f"({ans})" in user_choice_chart:
                            st.balloons() # 答對進階題才有氣球！
                            st.success(f"🎉 太強了！圖表題也答對！")
                            st.info(f"詳解：{chart_data['explanation']}")
                        else:
                            st.error(f"❌ 答錯了！正確答案是 {ans}")
                            st.info(f"詳解：{chart_data['explanation']}")
                    else:

                        st.warning("請先作答！")

