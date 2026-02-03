import streamlit as st
import json
import os
import glob
import pandas as pd
import plotly.graph_objects as go
import random
from datetime import datetime, date
# === 1. 頁面基礎設定 ===
st.set_page_config(
    page_title="分科測驗素養練習",
    page_icon="🧬",
    layout="wide", # 使用寬螢幕模式
    initial_sidebar_state="expanded"
)

# === ✨ 新增功能：使用者進度存檔系統 ===
USER_DATA_FILE = "user_progress.json"

def load_user_progress():
    """讀取使用者的閱讀進度與收藏"""
    if not os.path.exists(USER_DATA_FILE):
        return {"read": [], "starred": []}
    try:
        with open(USER_DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {"read": [], "starred": []}

def save_user_progress(data):
    """儲存進度到本地檔案"""
    with open(USER_DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def toggle_status(article_id, list_type):
    """切換狀態 (已讀/收藏)"""
    data = load_user_progress()
    current_list = data.get(list_type, [])
    
    if article_id in current_list:
        current_list.remove(article_id) # 如果有了就移除 (取消)
    else:
        current_list.append(article_id) # 如果沒有就加入
    
    data[list_type] = current_list
    save_user_progress(data)

# === 2. 核心邏輯：讀取資料庫 ===
def load_articles():
    base_dir = "articles"
    if not os.path.exists(base_dir):
        return []

    files = glob.glob(f"{base_dir}/**/*.json", recursive=True)
    
    articles = []
    for filepath in files:
        if os.path.isfile(filepath):
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    
                    folder_name = os.path.basename(os.path.dirname(filepath))
                    data['subject_category'] = folder_name
                    data['filepath'] = filepath
                    
                    # 確保每個文章都有 ID，如果沒有就用檔名代替
                    if 'id' not in data:
                        data['id'] = os.path.basename(filepath)
                    
                    articles.append(data)
            except Exception as e:
                print(f"Error loading {filepath}: {e}")
                continue
    
    articles.sort(key=lambda x: x.get('id', ''), reverse=True)
    return articles

def get_subject_emoji(subject):
    if "physics" in subject: return "⚛️"
    if "chemistry" in subject: return "⚗️"
    if "biology" in subject: return "🧬"
    return "📄"

# === 3. 介面佈局 ===

# 載入文章資料
all_articles = load_articles()

# ✨ 載入使用者進度
user_progress = load_user_progress()
read_ids = set(user_progress.get("read", []))
starred_ids = set(user_progress.get("starred", []))

# 側邊欄：標題與篩選
with st.sidebar:
    st.title("🔬 科普日報")
    st.markdown("針對**分科測驗**素養題設計的閱讀網站")
    st.markdown("### 🧭 導覽")
    page_mode = st.radio(
        "前往：",
        ["🏠 首頁 (Home)", "📖 開始閱讀 (Articles)"],
        label_visibility="collapsed"
    )
    st.divider()
    st.subheader("🏆 學習里程碑")
    
    total_articles = len(all_articles)
    read_count = len(read_ids)
    
    # 計算總進度
    if total_articles > 0:
        overall_progress = read_count / total_articles
        st.write(f"**總進度**：{int(overall_progress*100)}%")
        st.progress(overall_progress)
        
        # 根據進度給予回饋文字
        if overall_progress == 1.0:
            st.success("🎓 恭喜畢業！全科制霸！")
        elif overall_progress == 0.5:
            st.info("不可中道而廢")
        elif overall_progress == 0.9:
            st.info("行百里者半九十")
        elif overall_progress == 0:
            st.info("🌱 千里之行，始於足下！")
    else:
        st.warning("尚無文章資料")

    # === ✨ 2. 分科詳細進度 (新增功能) ===
    st.markdown("---")
    st.markdown("#### 科目進度")

    # 初始化統計字典
    # key 必須對應資料夾名稱
    sub_stats = {
        "physics":   {"name": "物理", "icon": "⚛️", "total": 0, "read": 0},
        "chemistry": {"name": "化學", "icon": "⚗️", "total": 0, "read": 0},
        "biology":   {"name": "生物", "icon": "🧬", "total": 0, "read": 0}
    }

    # 統計數據邏輯
    for a in all_articles:
        cat = a.get('subject_category', '')
        # 確保這個科目在我們的統計名單內 (避免未知的資料夾報錯)
        if cat in sub_stats:
            sub_stats[cat]["total"] += 1
            if a['id'] in read_ids:
                sub_stats[cat]["read"] += 1
    
    # 顯示各科進度條
    for cat, data in sub_stats.items():
        # 避免分母為 0
        if data["total"] > 0:
            p = data["read"] / data["total"]
            # 顯示格式： ⚛️ 物理 (3/10)
            label = f"{data['icon']} **{data['name']}** ({data['read']}/{data['total']})"
            st.markdown(label) 
            st.progress(p)
        else:
            # 如果該科目沒有文章，就不顯示進度條，或者顯示無資料
            st.caption(f"{data['icon']} {data['name']}：暫無文章")

    st.divider()
    
    if st.button("🔄 重新載入資料庫", key="reload_sidebar"):
        st.rerun()
    # ✨ 顯示統計數據
    c1, c2 , c3= st.columns(3)
    c1.metric("已讀", len(read_ids))
    c2.metric("收藏", len(starred_ids))
    c3.metric("收錄文章",len(all_articles))
    st.divider()
    if page_mode == "📖 開始閱讀 (Articles)":
        st.markdown("### 🛠️ 列表設定")
        subject_filter = st.radio(
            "選擇科目資料夾：",
            ["全部顯示", "physics (物理)", "chemistry (化學)", "biology (生物)","✅ 已讀文章", "⭐ 我的收藏"], # 新增收藏篩選
            index=0
        )
    
    if st.button("🔄 重新載入資料庫"):
        st.rerun()

    st.divider()
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
        st.caption("© 分科測驗科普日報")
        st.caption("台南一中 李安哲 ")
if page_mode == "🏠 首頁 (Home)":
    # === 首頁設計 ===
    
    # 1. 標題與簡介區 (左文右圖)
    col_intro, col_logo = st.columns([2, 1])
    
    with col_intro:
        st.title("🚀 前沿科普日報")
        st.markdown("#### 為分科測驗考生打造的 AI 陪讀助手")
        st.info("""
        **歡迎來到您的個人化科學閱讀站！**
        
        本系統利用 AI 技術，每日從全球頂尖學術期刊（如 Nature, Science）抓取最新研究，
        並將其轉譯為**高中物理、化學、生物**的科普文章與模擬試題。
        
        🎯 **核心功能：**
        * **最新新知**：不再死背課本，連結真實世界的研究。
        * **素養題庫**：每篇文章附帶 AI 生成的圖表題與觀念題。
        * **進度追蹤**：自動記錄您的學習軌跡，視覺化呈現強弱項。
        """)
        

    # 設定考試日期 (假設分科測驗為每年 7 月 12 日，可自行修改)
    today = date.today()
    current_year = today.year
    exam_date = date(current_year, 7, 11) # 設定今年考試日期
    
    # 如果今天已經過了今年的考試日期，就改成明年
    if today > exam_date:
        exam_date = date(current_year + 1, 7, 12)
        
    days_left = (exam_date - today).days

    # 使用 Container 包裝讓視覺更集中
    with st.container():
        # 顯示倒數天數 (使用 Metric 元件，視覺效果好)
        # delta_color="inverse" 會讓數字變紅 (代表時間緊迫) 或綠色
        
        st.metric(
            label=f"⏳ 距離 {exam_date.year} 分科測驗", 
            value=f"{days_left} 天",
            delta="-1 天", # 每天少一天
            delta_color="inverse" 
        )
        
        # 顯示日曆 (使用 date_input 當作日曆檢視器)
        st.date_input("📅 今日日期", today, disabled=True) # disabled=True 讓它變成唯讀模式
    st.divider()

    # 2. 系統運作流程圖
    st.subheader("⚙️ 系統運作流程")
    st.markdown("本系統如何將艱澀的論文轉化為您的考前與讀教材？")
    st.image("logic.png", width=500)
    st.divider()
    
    # 3. 快速開始按鈕
    c1, c2, c3 = st.columns([1,2,1])
    with c2:
        st.success("準備好開始學習了嗎？")
        # 這裡用一個提示，因為 Streamlit 的 radio 很難用按鈕直接連動切換
        st.markdown("### 👈 請點擊左側側邊欄的「📖 開始閱讀」進入文章列表")

elif page_mode == "📖 開始閱讀 (Articles)":
    # === 閱讀頁面邏輯 (原本的主程式) ===
    
    if not all_articles:
        st.warning("📭 資料庫是空的！請先執行後端腳本抓取論文。")
    else:
        if subject_filter == "全部顯示":
            filtered_articles = all_articles
        elif subject_filter == "⭐ 我的收藏":
            filtered_articles = [a for a in all_articles if a['id'] in starred_ids]
        elif subject_filter == "✅ 已讀文章":
            filtered_articles = [a for a in all_articles if a['id'] in read_ids]
        else:
            target_sub = subject_filter.split(" ")[0]
            filtered_articles = [a for a in all_articles if a['subject_category'] == target_sub]

        
        filtered_articles.sort(key=lambda x: x['id'] in read_ids)

        if not filtered_articles:
            st.info("此分類目前沒有文章。")
        else:
            # 雙欄佈局：選單 vs 內容
            col_menu, col_content = st.columns([1, 2.5])

            with col_menu:
                st.subheader("📚 文章選單")
                options = {}
                for index, a in enumerate(filtered_articles):
                    aid = a['id']
                    status_icons = ""
                    if aid in starred_ids: status_icons += "⭐"
                    if aid in read_ids: status_icons += "✅"

                    label = f"{get_subject_emoji(a['subject_category'])} {status_icons} {a['meta']['published']} | {a['meta']['title']}"
                    options[index] = label
                
                selected_index = st.radio(
                    "文章列表：",
                    options=options.keys(),
                    format_func=lambda x: options[x],
                    label_visibility="collapsed"
                )

            with col_content:
                article = filtered_articles[selected_index]
                meta = article['meta']
                content = article['content']
                aid = article['id']
                
                is_read = aid in read_ids
                is_starred = aid in starred_ids
                status_container = st.container()
                with status_container:
                    if is_read:
                        st.success(f"✅ **已讀完**｜你已經完成這篇 {article['subject_category']} 文章的學習！")
                    else:
                        st.warning("⏳ **未讀**｜這篇文章尚未閱讀，讀完記得標示已讀喔！")
                # === ✨ 操作按鈕區 (Action Bar) ===
                # 使用 container 讓按鈕排版更整齊
                with st.container():
                    st.markdown(f"### {meta.get('title', '無標題')}")
                    
                    # 狀態判斷
                    is_read = aid in read_ids
                    is_starred = aid in starred_ids
                    
                    col_btn1, col_btn2, col_info = st.columns([1, 1, 3])
                    
                    with col_btn1:
                        # 收藏按鈕
                        btn_label = "★ 取消收藏" if is_starred else "☆ 加入收藏"
                        btn_type = "primary" if is_starred else "secondary"
                        if st.button(btn_label, key=f"star_{aid}", type=btn_type):
                            toggle_status(aid, "starred")
                            st.rerun() # 重新整理以更新介面

                    with col_btn2:
                        # 已讀按鈕
                        read_label = "✅ 標示未讀" if is_read else "⭕ 標示已讀"
                        if st.button(read_label, key=f"read_{aid}"):
                            toggle_status(aid, "read")
                            st.rerun() # 重新整理以更新介面
                    
                    st.divider()

                # 顯示文章資訊
                c1, c2, c3 = st.columns(3)
                with c1: st.caption(f"**科目：** {article['subject_category'].upper()}")
                with c2: st.caption(f"**日期：** {meta.get('published', '未知')}")
                with c3: st.caption(f"**來源：** [{meta.get('source')}]({meta.get('url', '#')})")
                
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
                
                # 如果這篇文章還沒讀過，且使用者滑到了底部(或看完了)，可以提示
                if not is_read:
                    st.caption("💡 閱讀完畢後，記得點擊上方的「標示已讀」喔！")

                # === 3. 互動式測驗區 (保持原本邏輯) ===
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
                            palette = [
                                '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', 
                                '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'
                            ] 

                            # === 針對不同類型加入不同的 Trace ===
                            if chart_type == "bar":
                                # 長條圖
                                fig.add_trace(go.Bar(
                                    x=c['data_x'],
                                    y=c['data_y'],
                                    name='Data',
                                    marker_color=random.choice(palette),
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
                                    marker=dict(size=10, color=random.choice(palette))
                                ))
                                
                            else:
                                # 預設：折線圖 (線 + 點)
                                fig.add_trace(go.Scatter(
                                    x=c['data_x'], 
                                    y=c['data_y'],
                                    mode='lines+markers',
                                    name='Data',
                                    line=dict(color=random.choice(palette), width=4),
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



