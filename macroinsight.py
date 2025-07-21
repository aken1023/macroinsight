import streamlit as st
import requests
import json
import os
from datetime import datetime
import pandas as pd
import plotly.graph_objects as go
import time
from dotenv import load_dotenv

# 載入 .env 文件
load_dotenv()

# 設置 Streamlit 端口
os.environ['STREAMLIT_SERVER_PORT'] = '8877'

def _convert_impact_to_score(impact):
    """將文字影響程度轉換為數值分數"""
    impact = impact.lower()
    if '極大' in impact or '顯著' in impact or '強烈' in impact:
        return 1.0
    elif '較大' in impact or '正面' in impact or '利多' in impact:
        return 0.75
    elif '中等' in impact or '中性' in impact:
        return 0.5
    elif '較小' in impact or '輕微' in impact:
        return 0.25
    elif '極小' in impact or '微弱' in impact:
        return 0.1
    else:
        return 0.5  # 默認中等影響

# 設置頁面配置
st.set_page_config(
    page_title="宏觀新聞分析工具",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定義 CSS 樣式
st.markdown("""
<style>
    /* 全局樣式 - 小清新風格 */
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #f8fdff, #e8f4f8);
        max-width: 1400px;
        margin: 0 auto;
        padding: 2rem;
        color: #2c3e50;
        font-family: 'Microsoft JhengHei', 'PingFang SC', sans-serif;
    }

    /* 標題樣式 - 溫和清新 */
    h1, h2, h3, h4, h5, h6 {
        color: #34495e;
        font-family: 'Microsoft JhengHei', sans-serif;
        margin: 1.5rem 0;
        font-weight: 500;
    }

    h1 {
        font-size: 2.5rem;
        text-align: center;
        padding-bottom: 1rem;
        border-bottom: 3px solid #3498db;
        margin-bottom: 2rem;
        color: #2980b9;
        background: linear-gradient(90deg, #3498db, #2ecc71);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    h2 {
        font-size: 1.8rem;
        color: #27ae60;
        margin-top: 2rem;
        position: relative;
    }

    h2:before {
        content: '';
        position: absolute;
        left: 0;
        bottom: -5px;
        width: 50px;
        height: 3px;
        background: linear-gradient(90deg, #3498db, #2ecc71);
        border-radius: 2px;
    }

    h3 {
        font-size: 1.4rem;
        color: #16a085;
    }

    /* 內容區塊樣式 - 清新卡片風格 */
    .content-block {
        background: rgba(255, 255, 255, 0.9);
        border: 1px solid rgba(52, 152, 219, 0.2);
        border-radius: 15px;
        padding: 2rem;
        margin: 1.5rem 0;
        box-shadow: 0 8px 30px rgba(52, 152, 219, 0.1);
        backdrop-filter: blur(10px);
    }

    /* 文本樣式 - 清新可讀 */
    p, li, span {
        color: #34495e;
        font-size: 1.1rem;
        line-height: 1.8;
        font-family: 'Microsoft JhengHei', sans-serif;
    }

    /* 輸入框樣式 - 清新風格 */
    .stTextArea > div > div > textarea {
        background: rgba(255, 255, 255, 0.9);
        border: 2px solid rgba(52, 152, 219, 0.3);
        border-radius: 12px;
        padding: 1.2rem;
        font-size: 1.1rem;
        color: #2c3e50;
        min-height: 150px;
        font-family: 'Microsoft JhengHei', sans-serif;
        box-shadow: 0 4px 15px rgba(52, 152, 219, 0.1);
    }

    .stTextArea > div > div > textarea:focus {
        border-color: #3498db;
        box-shadow: 0 0 20px rgba(52, 152, 219, 0.3);
        outline: none;
    }

    /* 按鈕樣式 - 清新漸變 */
    .stButton > button {
        width: 100%;
        max-width: 300px;
        padding: 0.9rem 1.8rem;
        font-size: 1.1rem;
        color: white;
        background: linear-gradient(135deg, #3498db, #2ecc71);
        border: none;
        border-radius: 25px;
        cursor: pointer;
        transition: all 0.3s ease;
        font-family: 'Microsoft JhengHei', sans-serif;
        font-weight: 500;
        box-shadow: 0 4px 15px rgba(52, 152, 219, 0.3);
    }

    .stButton > button:hover {
        background: linear-gradient(135deg, #2980b9, #27ae60);
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(52, 152, 219, 0.4);
    }

    /* 表格樣式 - 清新風格 */
    .dataframe {
        width: 100%;
        border-collapse: separate;
        border-spacing: 0;
        margin: 1.5rem 0;
        background: rgba(255, 255, 255, 0.9);
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 4px 20px rgba(52, 152, 219, 0.1);
    }

    .dataframe th {
        background: linear-gradient(135deg, #74b9ff, #55efc4);
        color: white;
        font-weight: 500;
        padding: 1rem;
        text-align: left;
        border: none;
    }

    .dataframe td {
        padding: 1rem;
        border-bottom: 1px solid rgba(52, 152, 219, 0.1);
        color: #2c3e50;
        background: rgba(255, 255, 255, 0.8);
    }

    .dataframe tr:hover {
        background: rgba(116, 185, 255, 0.1);
    }

    /* 隱藏側邊欄 */
    [data-testid="stSidebar"] {
        display: none !important;
    }

    /* 分析結果區塊 - 清新卡片風格 */
    .analysis-section {
        background: rgba(255, 255, 255, 0.95);
        border: 1px solid rgba(116, 185, 255, 0.2);
        border-radius: 16px;
        padding: 2rem;
        margin: 2rem 0;
        box-shadow: 0 8px 30px rgba(116, 185, 255, 0.15);
        backdrop-filter: blur(10px);
    }

    .analysis-section h3 {
        color: #16a085;
        border-bottom: 2px solid rgba(22, 160, 133, 0.3);
        padding-bottom: 0.5rem;
        margin-bottom: 1.5rem;
    }

    /* 影響程度標籤 - 清新風格 */
    .impact-label {
        display: inline-block;
        padding: 0.5rem 1.2rem;
        border-radius: 20px;
        font-weight: 500;
        margin: 0.3rem;
        background: linear-gradient(135deg, #74b9ff, #55efc4);
        border: none;
        color: white;
        box-shadow: 0 2px 10px rgba(116, 185, 255, 0.2);
    }

    /* 圖表容器 - 清新風格 */
    [data-testid="stPlotlyChart"] {
        background: rgba(255, 255, 255, 0.95);
        border: 1px solid rgba(116, 185, 255, 0.2);
        border-radius: 16px;
        padding: 1.5rem;
        margin: 1.5rem 0;
        box-shadow: 0 6px 25px rgba(116, 185, 255, 0.1);
        backdrop-filter: blur(10px);
    }

    /* 提示框樣式 - 清新風格 */
    .stAlert {
        background: rgba(255, 255, 255, 0.9);
        color: #2c3e50;
        border: 1px solid rgba(116, 185, 255, 0.3);
        border-radius: 12px;
        padding: 1rem;
        box-shadow: 0 4px 15px rgba(116, 185, 255, 0.1);
    }

    /* 成功消息樣式 - 清新風格 */
    .success {
        background: linear-gradient(135deg, #55efc4, #81ecec);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 1rem;
        box-shadow: 0 4px 15px rgba(85, 239, 196, 0.2);
    }

    /* 選擇框樣式 - 清新風格 */
    .stSelectbox > div > div {
        background: rgba(255, 255, 255, 0.9);
        border: 1px solid rgba(116, 185, 255, 0.3);
        border-radius: 12px;
        box-shadow: 0 2px 10px rgba(116, 185, 255, 0.1);
    }

    .stSelectbox > div > div > div {
        color: #2c3e50;
    }

    /* 頁腳樣式 - 清新風格 */
    .footer {
        text-align: center;
        padding: 2rem;
        margin-top: 3rem;
        border-top: 1px solid rgba(116, 185, 255, 0.2);
        color: #7f8c8d;
        background: linear-gradient(135deg, 
                                    rgba(255,255,255,0.1), 
                                    rgba(116, 185, 255, 0.05));
        border-radius: 16px 16px 0 0;
    }

    /* 數據指標樣式 - 清新風格 */
    [data-testid="stMetricValue"] {
        color: #16a085 !important;
        font-size: 1.5rem !important;
        font-weight: 600 !important;
    }

    [data-testid="stMetricDelta"] {
        color: #27ae60 !important;
        font-size: 1rem !important;
    }

    /* 標籤頁樣式 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: rgba(255, 255, 255, 0.05);
        padding: 0.5rem;
        border-radius: 8px;
    }

    .stTabs [data-baseweb="tab"] {
        background: transparent;
        color: #e0e0e0;
        border: 1px solid rgba(0, 255, 204, 0.3);
        border-radius: 6px;
        padding: 0.5rem 1rem;
    }

    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(0, 255, 204, 0.1);
        color: #00ffcc;
    }

    .stTabs [aria-selected="true"] {
        background: rgba(0, 255, 204, 0.2) !important;
        color: #00ffcc !important;
    }

    /* 響應式設計 */
    @media screen and (max-width: 768px) {
        [data-testid="stAppViewContainer"] {
            padding: 1rem;
        }

        .content-block, .analysis-section {
            padding: 1.5rem;
        }

        h1 {
            font-size: 2rem;
        }

        h2 {
            font-size: 1.5rem;
        }

        h3 {
            font-size: 1.2rem;
        }

        p, li, span {
            font-size: 1rem;
        }

        .stButton > button {
            padding: 0.6rem 1.2rem;
            font-size: 1rem;
        }
    }

    /* 確保所有文字顏色 */
    [data-testid="stMarkdownContainer"] {
        color: #e0e0e0;
    }

    .stMarkdown, .stText {
        color: #e0e0e0;
    }

    /* 圖表標題樣式 */
    .js-plotly-plot .plotly .gtitle {
        fill: #00ffcc !important;
        font-family: 'Microsoft JhengHei', sans-serif !important;
    }

    /* 滾動條樣式 */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }

    ::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.05);
    }

    ::-webkit-scrollbar-thumb {
        background: rgba(0, 255, 204, 0.3);
        border-radius: 4px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: rgba(0, 255, 204, 0.5);
    }
</style>
""", unsafe_allow_html=True)

# 從 .env 文件讀取 API Key（不顯示在UI中）
api_key = os.getenv("DeepSeek_API")

# 預設分析選項
detailed_analysis = True
include_charts = True

# 主页面
st.markdown('<h1>🌸 宏觀新聞分析工具</h1>', unsafe_allow_html=True)
st.markdown(
    '<div class="content-block">💡 通過AI深度分析宏觀經濟新聞對金融市場的潛在影響，'
    '為企業投資與決策提供專業參考</div>',
    unsafe_allow_html=True
)

# 檢查API Key狀態
if not api_key:
    st.error("⚠️ 未找到 DeepSeek API Key，請檢查 .env 文件配置")
    st.info("📋 請確保 .env 文件中包含：\nDeepSeek_API=\"您的API密鑰\"")

# 台灣今日重要新聞列表
st.markdown("## 📰 今日台灣重要新聞")
st.markdown("*點選新聞標題即可進行分析*")

# 定義新聞數據
taiwan_news = [
    {
        "title": "TSMC 計劃建設四個新廠房，2028年底正式投產2奈米晶片",
        "content": ("台積電計劃今年底開始建設四個新廠房，目標在2028年底正式投產2奈米半導體晶圓。"
                    "中科管理局局長許茂新在中科22週年慶祝活動上宣布，園區第二期擴建將先建設滯洪池等水土保持設施。"
                    "台積電已正式租用土地，中科已交付。四個廠房位於中科園區，編號為Fab 25，"
                    "將包含四座1.4奈米晶圓製造廠。這項投資將進一步鞏固台灣在全球半導體產業的領導地位。"),
        "category": "科技"
    },
    {
        "title": "台股開戶數創新高，儘管面臨美國關稅威脅",
        "content": ("台灣證券交易所數據顯示，上個月股票交易開戶數達到1348萬戶的新高，"
                   "較5月底增加約3.2萬戶，較年初增加26.4萬戶。"
                   "儘管市場受到川普關稅政策影響，投資人情緒仍保持活躍。"
                   "61歲以上投資者開戶數增長最多，上半年增加22.5萬戶，佔總開戶數的29.92%。"
                   "今年上半年台股下跌779.08點，但投資人參與度依然提升。"),
        "category": "金融"
    },
    {
        "title": "央行總裁楊金龍：投機推升新台幣急升",
        "content": ("央行總裁楊金龍表示，市場投機是新台幣急升的主因，"
                   "呼籲出口商和金融機構保持冷靜，避免恐慌性拋售美元。"
                   "新台幣兌美元收盤大漲0.919元至30.145元，盤中最高升至29.59元。"
                   "楊金龍強調，匯率並非美台貿易談判議程，否認存在馬阿拉哥協議。"
                   "台灣第一季GDP表現優於預期，加上美國經濟疲軟跡象，促使全球資金回流新興市場。"),
        "category": "貨幣政策"
    },
    {
        "title": "中華經濟研究院上調年度GDP成長預測至3.05%",
        "content": ("中華經濟研究院將今年GDP成長預測上調至3.05%，基於上半年強勁表現，"
                   "但警告美國關稅威脅可能拖累下半年成長動能。"
                   "院長連賢明表示，上半年表現異常強勁，出口激增34.1%，民間投資成長7.03%，超出預期。"
                   "然而川普政策的不可預測性為經濟前景帶來下行風險。"),
        "category": "經濟預測"
    },
    {
        "title": "美國批准Nvidia對中國銷售H20 GPU",
        "content": ("Nvidia執行長黃仁勳宣布，川普政府已批准該公司向中國銷售用於AI開發的先進H20圖形處理器。"
                   "這項決定在Nvidia部落格文章中公布，黃仁勳也在中國官方媒體上談論此事。"
                   "美國政府向Nvidia保證將發放許可證，公司希望儘快開始交付。"
                   "中國企業在消息公布後立即搶購H20 GPU。"),
        "category": "科技貿易"
    },
    {
        "title": "川普準備實施產業特定關稅",
        "content": ("美國總統川普準備在下週五實施產業特定關稅，銅製品將面臨50%關稅。"
                   "這些關稅將與針對100多個國家的「對等」關稅同時生效。"
                   "川普表示可能在月底對製藥業實施關稅，半導體關稅也可能很快實施。"
                   "台積電曾警告，對台灣半導體的關稅可能減少晶片需求，危及其在亞利桑那州165億美元的投資計劃。"),
        "category": "貿易政策"
    }
]

# 創建新聞選擇區域
selected_news = None
cols = st.columns(2)

for i, news in enumerate(taiwan_news):
    col = cols[i % 2]
    with col:
        if st.button(
            f"📑 {news['title'][:50]}{'...' if len(news['title']) > 50 else ''}",
            key=f"news_{i}",
            help=f"類別：{news['category']}"
        ):
            selected_news = news

# 如果有選擇的新聞，自動填入分析區域
if selected_news:
    st.success(f"✅ 已選擇新聞：{selected_news['title']}")
    news_content = f"""
**新聞標題：** {selected_news['title']}
**新聞類別：** {selected_news['category']}

**新聞內容：**
{selected_news['content']}
"""
else:
    news_content = ""

# 新闻输入区域
news_text = st.text_area(
    "輸入宏觀經濟/金融新聞內容",
    value=news_content,
    height=200,
    help="粘貼完整的新聞文本，包括標題和正文內容，或點選上方新聞進行分析"
)

def analyze_news(news_text):
    try:
        # 定義分析結果的 JSON 結構模板
        result_template = {
            "summary": {
                "key_points": ["重點1", "重點2", "重點3"],
                "key_data": ["數據1", "數據2", "數據3"],
                "related_entities": ["相關企業/產業1", "相關企業/產業2"]
            },
            "market_impact": {
                "macro_economy": {
                    "gdp": {"impact": "影響程度", "description": "詳細說明"},
                    "inflation": {"impact": "影響程度", "description": "詳細說明"},
                    "employment": {"impact": "影響程度", "description": "詳細說明"},
                    "consumption": {"impact": "影響程度", "description": "詳細說明"}
                },
                "financial_markets": {
                    "stock_market": {
                        "indices": [{"name": "指數名稱", "impact": "影響", "target": "目標價位"}],
                        "sectors": [{"name": "產業名稱", "impact": "影響", "reason": "原因"}]
                    },
                    "bond_market": {
                        "government": {"impact": "影響", "yield_trend": "殖利率走勢"},
                        "corporate": {"impact": "影響", "spread_trend": "利差走勢"}
                    },
                    "forex_market": [
                        {"pair": "貨幣對", "impact": "影響", "target": "目標價位"}
                    ],
                    "commodities": [
                        {"name": "商品名稱", "impact": "影響", "target": "目標價位"}
                    ]
                }
            },
            "industry_impact": {
                "benefited": [
                    {"industry": "產業名稱", "reason": "受惠原因", "duration": "影響時長"}
                ],
                "damaged": [
                    {"industry": "產業名稱", "reason": "受損原因", "duration": "影響時長"}
                ],
                "supply_chain": {"description": "產業鏈影響說明"},
                "competition": {"description": "競爭格局變化說明"}
            },
            "corporate_impact": {
                "direct": [
                    {"company": "公司名稱", "impact": "影響", "action": "建議行動"}
                ],
                "indirect": [
                    {"company": "公司名稱", "impact": "影響", "action": "建議行動"}
                ],
                "opportunities": ["機會1", "機會2"],
                "risks": ["風險1", "風險2"]
            },
            "investment_advice": {
                "short_term": {
                    "position": ["建議1", "建議2"],
                    "risk_control": ["風控建議1", "風控建議2"],
                    "timing": ["時點建議1", "時點建議2"]
                },
                "long_term": {
                    "asset_allocation": ["配置建議1", "配置建議2"],
                    "sector_strategy": ["產業建議1", "產業建議2"],
                    "targets": ["投資標的1", "投資標的2"]
                }
            },
            "risk_warning": {
                "primary_risks": ["主要風險1", "主要風險2"],
                "secondary_risks": ["次要風險1", "次要風險2"],
                "monitoring_indicators": ["監控指標1", "監控指標2"],
                "hedging_suggestions": ["對沖建議1", "對沖建議2"]
            }
        }

        # 構建優化後的提示詞
        prompt = f"""
        請以專業財經分析師的角度，以台灣的經濟環境看待對以下新聞進行深入分析：

        "{news_text}"

        請從以下維度進行分析：

        1. 新聞重點摘要：
           - 核心要點（3-5點）
           - 關鍵數據和指標
           - 相關企業和產業

        2. 市場影響分析：
           A. 總體經濟影響
              - GDP影響
              - 通膨影響
              - 就業影響
              - 消費影響
           
           B. 金融市場影響
              - 股市影響（主要指數、產業、個股）
              - 債券市場影響（公債殖利率、信用債券）
              - 匯率影響（主要貨幣對）
              - 大宗商品影響（原物料、能源、貴金屬）

        3. 產業影響評估：
           - 受惠產業及原因
           - 受損產業及原因
           - 產業鏈上下游影響
           - 競爭格局變化

        4. 企業影響分析：
           - 直接影響企業
           - 間接影響企業
           - 潛在商機與風險
           - 企業因應策略建議

        5. 投資建議：
           A. 短期策略（1-3個月）
              - 投資部位建議
              - 風險規避建議
              - 操作時點建議
           
           B. 中長期策略（3個月以上）
              - 資產配置建議
              - 產業布局建議
              - 投資標的建議

        6. 風險提示：
           - 主要風險因素
           - 次要風險因素
           - 風險監控指標
           - 風險對沖建議

        請嚴格按照以下 JSON 格式返回分析結果，不要添加任何其他文字：
        {json.dumps(result_template, ensure_ascii=False, indent=2)}
        """

        # 調用 DeepSeek API
        url = "https://api.deepseek.com/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        data = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3,
            "max_tokens": 4000
        }

        response = requests.post(url, headers=headers, data=json.dumps(data))

        if response.status_code == 200:
            result = response.json()
            response_content = result["choices"][0]["message"]["content"]
            
            # 嘗試找到並提取 JSON 部分
            try:
                # 查找第一個 { 和最後一個 } 的位置
                start_idx = response_content.find('{')
                end_idx = response_content.rfind('}') + 1
                
                if start_idx >= 0 and end_idx > start_idx:
                    json_str = response_content[start_idx:end_idx]
                    try:
                        analysis = json.loads(json_str)
                        return analysis
                    except json.JSONDecodeError as je:
                        st.error(f"JSON 解析錯誤: {str(je)}")
                        st.text("API 返回的原始內容:")
                        st.code(response_content)
                        return None
                else:
                    st.error("無法在回應中找到有效的 JSON 結構")
                    st.text("API 返回的原始內容:")
                    st.code(response_content)
                    return None
            except Exception as e:
                st.error(f"處理 API 回應時出錯: {str(e)}")
                st.text("API 返回的原始內容:")
                st.code(response_content)
                return None
        else:
            st.error(f"API 調用失敗: {response.status_code}")
            st.text(f"錯誤詳情: {response.text}")
            return None

    except Exception as e:
        st.error(f"分析過程中出現錯誤: {str(e)}")
        return None

# 分析按钮
if st.button("分析新聞", disabled=not news_text or not api_key):
    if not news_text:
        st.error("請輸入新聞內容")
    elif not api_key:
        st.error("請輸入 DeepSeek API Key")
    else:
        with st.spinner("正在進行深度分析，請稍候..."):
            analysis = analyze_news(news_text)
            
            if analysis:
                # 顯示新聞重點
                st.header("新聞重點摘要")
                with st.container():
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.subheader("核心要點")
                        for point in analysis["summary"]["key_points"]:
                            st.markdown(f"• {point}")
                    
                    with col2:
                        st.subheader("關鍵數據")
                        for data in analysis["summary"]["key_data"]:
                            st.markdown(f"• {data}")

                # 市場影響分析
                st.header("市場影響分析")
                
                # 總體經濟影響
                st.subheader("總體經濟影響")
                macro = analysis["market_impact"]["macro_economy"]
                cols = st.columns(4)
                
                with cols[0]:
                    st.metric("GDP影響", macro["gdp"]["impact"])
                    st.caption(macro["gdp"]["description"])
                
                with cols[1]:
                    st.metric("通膨影響", macro["inflation"]["impact"])
                    st.caption(macro["inflation"]["description"])
                
                with cols[2]:
                    st.metric("就業影響", macro["employment"]["impact"])
                    st.caption(macro["employment"]["description"])
                
                with cols[3]:
                    st.metric("消費影響", macro["consumption"]["impact"])
                    st.caption(macro["consumption"]["description"])

                # 金融市場影響
                st.subheader("金融市場影響")
                tabs = st.tabs(["股市", "債市", "匯市", "商品"])
                
                with tabs[0]:
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("##### 主要指數影響")
                        for index in analysis["market_impact"]["financial_markets"]["stock_market"]["indices"]:
                            st.metric(index["name"], index["impact"], index["target"])
                    
                    with col2:
                        st.markdown("##### 產業影響")
                        for sector in analysis["market_impact"]["financial_markets"]["stock_market"]["sectors"]:
                            st.metric(sector["name"], sector["impact"])
                            st.caption(sector["reason"])

                with tabs[1]:
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("##### 公債市場")
                        bond = analysis["market_impact"]["financial_markets"]["bond_market"]["government"]
                        st.metric("影響", bond["impact"])
                        st.caption(f"殖利率走勢：{bond['yield_trend']}")
                    
                    with col2:
                        st.markdown("##### 公司債市場")
                        corp = analysis["market_impact"]["financial_markets"]["bond_market"]["corporate"]
                        st.metric("影響", corp["impact"])
                        st.caption(f"利差走勢：{corp['spread_trend']}")

                with tabs[2]:
                    st.markdown("##### 主要貨幣對影響")
                    cols = st.columns(3)
                    for i, pair in enumerate(analysis["market_impact"]["financial_markets"]["forex_market"]):
                        with cols[i % 3]:
                            st.metric(pair["pair"], pair["impact"], pair["target"])

                with tabs[3]:
                    st.markdown("##### 大宗商品影響")
                    cols = st.columns(3)
                    for i, commodity in enumerate(analysis["market_impact"]["financial_markets"]["commodities"]):
                        with cols[i % 3]:
                            st.metric(commodity["name"], commodity["impact"], commodity["target"])

                # 產業影響
                st.header("產業影響評估")
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("受惠產業")
                    for industry in analysis["industry_impact"]["benefited"]:
                        with st.expander(f"{industry['industry']} ({industry['duration']})"):
                            st.write(industry["reason"])

                with col2:
                    st.subheader("受損產業")
                    for industry in analysis["industry_impact"]["damaged"]:
                        with st.expander(f"{industry['industry']} ({industry['duration']})"):
                            st.write(industry["reason"])

                st.markdown("##### 產業鏈影響")
                st.info(analysis["industry_impact"]["supply_chain"]["description"])
                
                st.markdown("##### 競爭格局變化")
                st.info(analysis["industry_impact"]["competition"]["description"])

                # 投資建議
                st.header("投資建議")
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("短期策略 (1-3個月)")
                    st.markdown("##### 投資部位")
                    for pos in analysis["investment_advice"]["short_term"]["position"]:
                        st.markdown(f"• {pos}")
                    
                    st.markdown("##### 風險控制")
                    for risk in analysis["investment_advice"]["short_term"]["risk_control"]:
                        st.markdown(f"• {risk}")
                    
                    st.markdown("##### 操作時點")
                    for timing in analysis["investment_advice"]["short_term"]["timing"]:
                        st.markdown(f"• {timing}")

                with col2:
                    st.subheader("中長期策略 (3個月以上)")
                    st.markdown("##### 資產配置")
                    for alloc in analysis["investment_advice"]["long_term"]["asset_allocation"]:
                        st.markdown(f"• {alloc}")
                    
                    st.markdown("##### 產業布局")
                    for sector in analysis["investment_advice"]["long_term"]["sector_strategy"]:
                        st.markdown(f"• {sector}")
                    
                    st.markdown("##### 投資標的")
                    for target in analysis["investment_advice"]["long_term"]["targets"]:
                        st.markdown(f"• {target}")

                # 風險提示
                st.header("風險提示")
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("主要風險")
                    for risk in analysis["risk_warning"]["primary_risks"]:
                        st.markdown(f"• {risk}")
                    
                    st.subheader("次要風險")
                    for risk in analysis["risk_warning"]["secondary_risks"]:
                        st.markdown(f"• {risk}")

                with col2:
                    st.subheader("風險監控指標")
                    for indicator in analysis["risk_warning"]["monitoring_indicators"]:
                        st.markdown(f"• {indicator}")
                    
                    st.subheader("風險對沖建議")
                    for hedge in analysis["risk_warning"]["hedging_suggestions"]:
                        st.markdown(f"• {hedge}")

                # 添加視覺化圖表
                if include_charts:
                    st.header("視覺化分析")
                    
                    # 1. 市場影響雷達圖
                    st.subheader("市場影響雷達圖")
                    
                    # 準備雷達圖數據
                    impact_scores = {
                        "GDP影響": _convert_impact_to_score(analysis["market_impact"]["macro_economy"]["gdp"]["impact"]),
                        "通膨影響": _convert_impact_to_score(analysis["market_impact"]["macro_economy"]["inflation"]["impact"]),
                        "就業影響": _convert_impact_to_score(analysis["market_impact"]["macro_economy"]["employment"]["impact"]),
                        "消費影響": _convert_impact_to_score(analysis["market_impact"]["macro_economy"]["consumption"]["impact"]),
                        "股市影響": _convert_impact_to_score(analysis["market_impact"]["financial_markets"]["stock_market"]["indices"][0]["impact"]),
                        "債市影響": _convert_impact_to_score(analysis["market_impact"]["financial_markets"]["bond_market"]["government"]["impact"])
                    }
                    
                    categories = list(impact_scores.keys())
                    values = list(impact_scores.values())

                    fig = go.Figure()
                    fig.add_trace(go.Scatterpolar(
                        r=values,
                        theta=categories,
                        fill='toself',
                        name='市場影響程度',
                        line_color='rgb(0, 0, 0)',
                        fillcolor='rgba(169, 169, 169, 0.3)'
                    ))

                    fig.update_layout(
                        polar=dict(
                            radialaxis=dict(
                                visible=True,
                                range=[0, 1],
                                tickvals=[0, 0.25, 0.5, 0.75, 1],
                                ticktext=['極小', '較小', '中等', '較大', '極大']
                            )
                        ),
                        showlegend=False,
                        title="各面向影響程度分析",
                        title_x=0.5
                    )

                    st.plotly_chart(fig, use_container_width=True)

                    # 2. 產業影響對比圖
                    st.subheader("產業影響對比")
                    
                    # 準備產業影響數據
                    benefited_industries = [industry["industry"] for industry in analysis["industry_impact"]["benefited"]]
                    damaged_industries = [industry["industry"] for industry in analysis["industry_impact"]["damaged"]]
                    
                    # 創建產業影響對比圖
                    fig_industries = go.Figure()
                    
                    # 受惠產業
                    fig_industries.add_trace(go.Bar(
                        name='受惠產業',
                        y=benefited_industries,
                        x=[0.8] * len(benefited_industries),
                        orientation='h',
                        marker_color='rgb(144, 238, 144)',
                        text=['正面影響'] * len(benefited_industries),
                        textposition='auto',
                    ))
                    
                    # 受損產業
                    fig_industries.add_trace(go.Bar(
                        name='受損產業',
                        y=damaged_industries,
                        x=[-0.8] * len(damaged_industries),
                        orientation='h',
                        marker_color='rgb(255, 182, 193)',
                        text=['負面影響'] * len(damaged_industries),
                        textposition='auto',
                    ))
                    
                    fig_industries.update_layout(
                        title="產業影響對比分析",
                        title_x=0.5,
                        barmode='relative',
                        yaxis=dict(title='產業'),
                        xaxis=dict(
                            title='影響程度',
                            tickvals=[-0.8, 0, 0.8],
                            ticktext=['負面', '中性', '正面'],
                            range=[-1, 1]
                        ),
                        showlegend=True
                    )
                    
                    st.plotly_chart(fig_industries, use_container_width=True)

                    # 3. 投資建議時間軸
                    st.subheader("投資建議時間軸")
                    
                    # 準備時間軸數據
                    timeline_data = {
                        '短期策略': analysis["investment_advice"]["short_term"]["position"],
                        '中長期策略': analysis["investment_advice"]["long_term"]["asset_allocation"]
                    }
                    
                    # 創建時間軸圖表
                    fig_timeline = go.Figure()
                    
                    y_positions = [0, 1]  # 短期和中長期的y軸位置
                    colors = ['rgb(169, 169, 169)', 'rgb(0, 0, 0)']
                    
                    for i, (period, strategies) in enumerate(timeline_data.items()):
                        for j, strategy in enumerate(strategies):
                            fig_timeline.add_trace(go.Scatter(
                                x=[j, j+0.8],
                                y=[y_positions[i], y_positions[i]],
                                mode='lines+text',
                                name=period if j == 0 else None,
                                text=[strategy, ''],
                                textposition='middle right',
                                line=dict(color=colors[i], width=2),
                                showlegend=j == 0
                            ))
                    
                    fig_timeline.update_layout(
                        title="投資策略時間軸",
                        title_x=0.5,
                        yaxis=dict(
                            ticktext=['短期', '中長期'],
                            tickvals=[0, 1],
                            zeroline=False
                        ),
                        xaxis=dict(
                            showticklabels=False,
                            zeroline=False
                        ),
                        showlegend=True,
                        height=400
                    )
                    
                    st.plotly_chart(fig_timeline, use_container_width=True)

                # 添加總結和建議部分
                st.markdown('<div class="sub-header">總結與投資建議</div>', unsafe_allow_html=True)

                # 生成總結建議
                summary_prompt = f"""
                基於以下宏觀新聞分析，提供簡明的投資建議總結：

                新聞內容: {news_text}

                核心要點: {', '.join(analysis['summary']['key_points'])}
                
                總體經濟影響:
                - GDP: {analysis['market_impact']['macro_economy']['gdp']['impact']}
                - 通膨: {analysis['market_impact']['macro_economy']['inflation']['impact']}
                - 就業: {analysis['market_impact']['macro_economy']['employment']['impact']}
                - 消費: {analysis['market_impact']['macro_economy']['consumption']['impact']}

                主要風險:
                {', '.join(analysis['risk_warning']['primary_risks'])}

                投資建議:
                短期: {', '.join(analysis['investment_advice']['short_term']['position'])}
                中長期: {', '.join(analysis['investment_advice']['long_term']['asset_allocation'])}

                請提供200字以內的投資建議總結，包括風險提示。
                """

                # 調用 DeepSeek API 獲取投資建議
                summary_data = {
                    "model": "deepseek-chat",
                    "messages": [
                        {"role": "user", "content": summary_prompt}
                    ],
                    "temperature": 0.3,
                    "max_tokens": 500
                }

                # 定義 API URL 和標頭
                api_url = "https://api.deepseek.com/v1/chat/completions"
                api_headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {api_key}"
                }

                summary_response = requests.post(api_url, headers=api_headers, data=json.dumps(summary_data))

                if summary_response.status_code == 200:
                    summary_result = summary_response.json()
                    investment_advice = summary_result["choices"][0]["message"]["content"]
                    st.markdown(f'<div class="info-box">{investment_advice}</div>', unsafe_allow_html=True)
                else:
                    st.error("無法生成投資建議總結")

                # 導出報告選項
                st.markdown('<div class="sub-header">導出分析報告</div>', unsafe_allow_html=True)

                # 生成完整報告文本
                report_text = f"""
                # 宏觀新聞影響分析報告

                ## 分析新聞
                {news_text}

                ## 新聞重點摘要
                ### 核心要點
                {chr(10).join([f"- {point}" for point in analysis['summary']['key_points']])}

                ### 關鍵數據
                {chr(10).join([f"- {data}" for data in analysis['summary']['key_data']])}

                ### 相關企業和產業
                {chr(10).join([f"- {entity}" for entity in analysis['summary']['related_entities']])}

                ## 市場影響分析

                ### 總體經濟影響
                - GDP影響: {analysis['market_impact']['macro_economy']['gdp']['impact']}
                  {analysis['market_impact']['macro_economy']['gdp']['description']}
                - 通膨影響: {analysis['market_impact']['macro_economy']['inflation']['impact']}
                  {analysis['market_impact']['macro_economy']['inflation']['description']}
                - 就業影響: {analysis['market_impact']['macro_economy']['employment']['impact']}
                  {analysis['market_impact']['macro_economy']['employment']['description']}
                - 消費影響: {analysis['market_impact']['macro_economy']['consumption']['impact']}
                  {analysis['market_impact']['macro_economy']['consumption']['description']}

                ### 金融市場影響

                #### 股票市場
                主要指數影響:
                {chr(10).join([f"- {index['name']}: {index['impact']} (目標: {index['target']})" for index in analysis['market_impact']['financial_markets']['stock_market']['indices']])}

                產業影響:
                {chr(10).join([f"- {sector['name']}: {sector['impact']} - {sector['reason']}" for sector in analysis['market_impact']['financial_markets']['stock_market']['sectors']])}

                #### 債券市場
                - 公債市場: {analysis['market_impact']['financial_markets']['bond_market']['government']['impact']}
                  殖利率走勢: {analysis['market_impact']['financial_markets']['bond_market']['government']['yield_trend']}
                - 公司債市場: {analysis['market_impact']['financial_markets']['bond_market']['corporate']['impact']}
                  利差走勢: {analysis['market_impact']['financial_markets']['bond_market']['corporate']['spread_trend']}

                #### 匯市影響
                {chr(10).join([f"- {pair['pair']}: {pair['impact']} (目標: {pair['target']})" for pair in analysis['market_impact']['financial_markets']['forex_market']])}

                #### 商品市場影響
                {chr(10).join([f"- {commodity['name']}: {commodity['impact']} (目標: {commodity['target']})" for commodity in analysis['market_impact']['financial_markets']['commodities']])}

                ## 產業影響評估

                ### 受惠產業
                {chr(10).join([f"- {industry['industry']} ({industry['duration']}): {industry['reason']}" for industry in analysis['industry_impact']['benefited']])}

                ### 受損產業
                {chr(10).join([f"- {industry['industry']} ({industry['duration']}): {industry['reason']}" for industry in analysis['industry_impact']['damaged']])}

                ### 產業鏈影響
                {analysis['industry_impact']['supply_chain']['description']}

                ### 競爭格局變化
                {analysis['industry_impact']['competition']['description']}

                ## 企業影響分析

                ### 直接影響企業
                {chr(10).join([f"- {company['company']}: {company['impact']} - {company['action']}" for company in analysis['corporate_impact']['direct']])}

                ### 間接影響企業
                {chr(10).join([f"- {company['company']}: {company['impact']} - {company['action']}" for company in analysis['corporate_impact']['indirect']])}

                ### 潛在商機
                {chr(10).join([f"- {opportunity}" for opportunity in analysis['corporate_impact']['opportunities']])}

                ### 潛在風險
                {chr(10).join([f"- {risk}" for risk in analysis['corporate_impact']['risks']])}

                ## 投資建議

                ### 短期策略 (1-3個月)
                
                投資部位:
                {chr(10).join([f"- {pos}" for pos in analysis['investment_advice']['short_term']['position']])}

                風險控制:
                {chr(10).join([f"- {risk}" for risk in analysis['investment_advice']['short_term']['risk_control']])}

                操作時點:
                {chr(10).join([f"- {timing}" for timing in analysis['investment_advice']['short_term']['timing']])}

                ### 中長期策略 (3個月以上)

                資產配置:
                {chr(10).join([f"- {alloc}" for alloc in analysis['investment_advice']['long_term']['asset_allocation']])}

                產業布局:
                {chr(10).join([f"- {sector}" for sector in analysis['investment_advice']['long_term']['sector_strategy']])}

                投資標的:
                {chr(10).join([f"- {target}" for target in analysis['investment_advice']['long_term']['targets']])}

                ## 風險提示

                ### 主要風險
                {chr(10).join([f"- {risk}" for risk in analysis['risk_warning']['primary_risks']])}

                ### 次要風險
                {chr(10).join([f"- {risk}" for risk in analysis['risk_warning']['secondary_risks']])}

                ### 風險監控指標
                {chr(10).join([f"- {indicator}" for indicator in analysis['risk_warning']['monitoring_indicators']])}

                ### 風險對沖建議
                {chr(10).join([f"- {hedge}" for hedge in analysis['risk_warning']['hedging_suggestions']])}

                ## 投資建議總結
                {investment_advice}

                ---
                *報告生成時間: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*
                *由 MacroInsight 宏觀新聞分析工具生成*
                """

                # 提供下載報告選項
                st.download_button(
                    label="下載完整分析報告 (Markdown)",
                    data=report_text,
                    file_name=f"宏觀新聞分析_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                    mime="text/markdown",
                )

# 添加頁腳
st.markdown('<div class="footer">作者:© 2025 AKEN | 基於HAI模型</div>',
            unsafe_allow_html=True)

