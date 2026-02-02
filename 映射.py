import json

# 這是我們精心設計的「課綱映射表」
# 結構：科目 -> 章節 -> 搜尋關鍵字列表 (包含主要概念與熱門研究領域)
syllabus_data = {
    "physics": {
        "力學 (Mechanics)": [
            "aerodynamics",           # 空氣動力學 (流體力學應用)
            "projectile motion",      # 拋體運動
            "collision dynamics",     # 碰撞動力學 (動量守恆)
            "planetary orbit"         # 行星軌道 (萬有引力)
        ],
        "電磁學 (Electromagnetism)": [
            "superconductor",         # 超導體 (電流磁效應延伸)
            "electromagnetic induction", # 電磁感應
            "hall effect",            # 霍爾效應
            "wireless power transfer" # 無線傳輸 (電磁波應用)
        ],
        "光學與波動 (Optics & Waves)": [
            "fiber optics",           # 光纖 (全反射)
            "doppler effect",         # 都卜勒效應
            "laser physics",          # 雷射
            "interference pattern"    # 干涉圖樣
        ],
        "近代物理 (Modern Physics)": [
            "quantum entanglement",   # 量子糾纏
            "photoelectric effect",   # 光電效應
            "nuclear fusion",         # 核融合
            "standard model physics"  # 標準模型
        ]
    },
    "chemistry": {
        "物質構造 (Structure of Matter)": [
            "molecular orbital theory", # 分子軌域理論
            "graphene structure",       # 石墨烯 (共價網狀固體)
            "crystal lattice",          # 晶格結構
            "coordination complex"      # 配位化合物
        ],
        "有機化學 (Organic Chemistry)": [
            "polymer degradation",      # 聚合物降解
            "catalytic synthesis",      # 催化合成
            "green chemistry",          # 綠色化學
            "drug delivery system"      # 藥物傳輸系統 (有機應用)
        ],
        "化學反應 (Chemical Reactions)": [
            "reaction kinetics",        # 反應動力學
            "electrochemical cell",     # 電化電池
            "entropy change",           # 熵變 (熱力學)
            "buffer solution"           # 緩衝溶液
        ]
    },
    "biology": {
        "細胞與遺傳 (Cell & Genetics)": [
            "CRISPR-Cas9",              # 基因編輯
            "mRNA vaccine",             # 信使核糖核酸疫苗
            "mitochondrial function",   # 線粒體功能
            "epigenetics"               # 表觀遺傳學
        ],
        "動物生理 (Animal Physiology)": [
            "neurotransmission",        # 神經傳導
            "T-cell immunity",          # T細胞免疫
            "circadian rhythm",         # 晝夜節律 (荷爾蒙)
            "synaptic plasticity"       # 突觸可塑性
        ],
        "生態與演化 (Ecology & Evolution)": [
            "biodiversity loss",        # 生物多樣性
            "carbon cycle",             # 碳循環
            "evolutionary adaptation",  # 演化適應
            "microbiome"                # 微生物組 (共生)
        ]
    }
}

# 將這個字典存檔為 JSON 文件，供後續步驟使用
file_name = "syllabus_mapping.json"
with open(file_name, "w", encoding="utf-8") as f:
    json.dump(syllabus_data, f, indent=4, ensure_ascii=False)

print(f"成功！已建立 {file_name}。")
print("這是你的關鍵字地圖，未來的 AI 將根據這個地圖去抓取文章。")