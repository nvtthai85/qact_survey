"""
🎓 AI Survey Analysis Dashboard
Dashboard phân tích khảo sát sinh viên với AI
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import json
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# ── Page config ───────────────────────────────────────────────
st.set_page_config(
    page_title="AI Survey Analytics | FPT Education",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

/* Base */
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

/* Vibrant Clean Light Background */
.stApp {
    background-color: #f8fafc !important;
    color: #0f172a !important;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #ffffff !important;
    border-right: 1px solid #e2e8f0 !important;
}

/* Cards */
.metric-card {
    background: #ffffff !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 16px !important;
    padding: 20px 24px !important;
    text-align: center !important;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03) !important;
    transition: all 0.3s ease !important;
}
.metric-card:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.08), 0 4px 6px -2px rgba(0, 0, 0, 0.04) !important;
}
.metric-number {
    font-size: 2.4rem !important;
    font-weight: 800 !important;
    background: linear-gradient(135deg, #ff6b00, #ec4899) !important;
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    line-height: 1.1 !important;
}
.metric-label {
    font-size: 0.82rem !important;
    color: #475569 !important;
    margin-top: 6px !important;
    font-weight: 600 !important;
    letter-spacing: 0.5px !important;
    text-transform: uppercase !important;
}

/* Section headers */
.section-header {
    display: flex !important;
    align-items: center !important;
    gap: 10px !important;
    font-size: 1.25rem !important;
    font-weight: 700 !important;
    color: #0f172a !important;
    margin: 28px 0 16px 0 !important;
    padding-bottom: 10px !important;
    border-bottom: 2px solid #ff6b00 !important;
}

/* Executive summary */
.exec-card {
    background: linear-gradient(135deg, rgba(255,107,0,0.06), rgba(236,72,153,0.03)) !important;
    border: 1px solid rgba(255,107,0,0.2) !important;
    border-radius: 20px !important;
    padding: 28px 32px !important;
    margin-bottom: 24px !important;
}
.exec-headline {
    font-size: 1.5rem !important;
    font-weight: 800 !important;
    color: #ff6b00 !important;
    margin-bottom: 12px !important;
}
.exec-overview { 
    color: #334155 !important; 
    line-height: 1.7 !important; 
}

/* Insight chips */
.insight-chip {
    display: inline-block !important;
    background: rgba(255,107,0,0.08) !important;
    border: 1px solid rgba(255,107,0,0.25) !important;
    border-radius: 20px !important;
    padding: 4px 14px !important;
    font-size: 0.8rem !important;
    color: #d97706 !important;
    margin: 3px !important;
    font-weight: 500 !important;
}

/* Strength / Bottleneck cards */
.strength-item {
    background: #ecfdf5 !important;
    border-left: 4px solid #10b981 !important;
    border-radius: 8px !important;
    padding: 14px 18px !important;
    margin-bottom: 10px !important;
    color: #065f46 !important;
    font-weight: 500 !important;
}
.bottleneck-item {
    background: #fef2f2 !important;
    border-left: 4px solid #ef4444 !important;
    border-radius: 8px !important;
    padding: 14px 18px !important;
    margin-bottom: 10px !important;
    color: #991b1b !important;
    font-weight: 500 !important;
}
.watch-item {
    background: #fffbeb !important;
    border-left: 4px solid #f59e0b !important;
    border-radius: 8px !important;
    padding: 14px 18px !important;
    margin-bottom: 10px !important;
    color: #92400e !important;
    font-weight: 500 !important;
}

/* Checklist rows */
.checklist-ok       { color: #059669 !important; font-weight: 700 !important; }
.checklist-warning  { color: #d97706 !important; font-weight: 700 !important; }
.checklist-critical { color: #dc2626 !important; font-weight: 800 !important; }

/* Action cards */
.action-high   { border-left: 4px solid #ef4444 !important; background: #fef2f2 !important; color: #991b1b !important; }
.action-medium { border-left: 4px solid #f59e0b !important; background: #fffbeb !important; color: #92400e !important; }
.action-low    { border-left: 4px solid #10b981 !important; background: #ecfdf5 !important; color: #065f46 !important; }
.action-card   { border-radius: 10px !important; padding: 14px 18px !important; margin-bottom: 10px !important; font-weight: 500 !important; }

/* Plotly chart bg */
.js-plotly-plot .plotly .bg { fill: transparent !important; }

/* Upload zone */
.uploadedFile { background: #ffffff !important; border: 1px solid #e2e8f0 !important; border-radius: 12px !important; }

/* Progress bar */
.stProgress > div > div { background: linear-gradient(90deg, #ff6b00, #ec4899) !important; }

/* Tabs */
.stTabs [data-baseweb="tab"] {
    color: #64748b !important;
    font-weight: 600 !important;
}
.stTabs [aria-selected="true"] {
    color: #ff6b00 !important;
    border-bottom-color: #ff6b00 !important;
}

/* Sidebar texts brightness */
[data-testid="stSidebar"] .stMarkdown p,
[data-testid="stSidebar"] .stMarkdown li,
[data-testid="stSidebar"] label p,
[data-testid="stSidebar"] small,
[data-testid="stSidebar"] .stWidgetLabel,
[data-testid="stSidebar"] .stMarkdown h1,
[data-testid="stSidebar"] .stMarkdown h2,
[data-testid="stSidebar"] .stMarkdown h3 {
    color: #1e293b !important;
    font-weight: 600 !important;
}
[data-testid="stSidebar"] strong {
    color: #0f172a !important;
    font-weight: 800 !important;
}

/* Fail-proof widget styling for Streamlit Cloud (preventing invisible text in light theme) */
div[data-baseweb="input"] {
    background-color: #f1f5f9 !important;
    border: 1px solid #cbd5e1 !important;
    border-radius: 8px !important;
}
div[data-baseweb="input"] input {
    color: #0f172a !important;
}
div[data-baseweb="select"] > div {
    background-color: #f1f5f9 !important;
    border: 1px solid #cbd5e1 !important;
    border-radius: 8px !important;
}
div[data-baseweb="select"] span,
div[data-baseweb="select"] div {
    color: #0f172a !important;
}
div[role="listbox"] {
    background-color: #ffffff !important;
    color: #0f172a !important;
    border: 1px solid #cbd5e1 !important;
}
div[role="option"] {
    color: #0f172a !important;
}

/* File Uploader override */
div[data-testid="stFileUploader"] {
    background-color: #f8fafc !important;
    border: 1px dashed #cbd5e1 !important;
    border-radius: 12px !important;
    padding: 12px !important;
}
div[data-testid="stFileUploader"] section,
div[data-testid="stFileUploaderDropzone"] {
    background-color: transparent !important;
    background: transparent !important;
    border: none !important;
}
div[data-testid="stFileUploader"] label p,
div[data-testid="stFileUploader"] div,
div[data-testid="stFileUploader"] span,
div[data-testid="stFileUploader"] small,
div[data-testid="stFileUploaderDropzone"] p,
div[data-testid="stFileUploaderDropzone"] span {
    color: #334155 !important;
}

/* Button overrides for light mode */
button[data-testid="stBaseButton-secondary"] {
    background-color: #ffffff !important;
    color: #1e293b !important;
    border: 1px solid #cbd5e1 !important;
}
button[data-testid="stBaseButton-secondary"]:hover {
    background-color: #f1f5f9 !important;
    border-color: #94a3b8 !important;
    color: #0f172a !important;
}
button[data-testid="stBaseButton-primary"] {
    background-color: #ff6b00 !important;
    color: #ffffff !important;
}
button[data-testid="stBaseButton-primary"]:hover {
    background-color: #e05e00 !important;
    color: #ffffff !important;
}

h1, h2, h3, h4, h5, h6 {
    color: #0f172a !important;
}
</style>
""", unsafe_allow_html=True)

# ── QUESTION MAP ─────────────────────────────────────────────
QUESTION_MAP = {
    "Q1": "Chương trình đào tạo",
    "Q2": "Tổ chức đào tạo",
    "Q3": "Tài nguyên & CSVC",
    "Q4": "Giảng dạy & GV",
    "Q5": "Tinh thần phục vụ",
    "Q6": "Hỗ trợ sinh viên",
    "Q7": "Hoạt động truyền thống",
    "Q8": "Tổng thể trải nghiệm",
}

CHART_COLORS = {
    "positive": "#34d399",
    "neutral":  "#60a5fa",
    "negative": "#f87171",
}
PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter", color="#0f172a"),
    margin=dict(t=40, b=20, l=20, r=20),
)


# ══════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("## 🎓 AI Survey Analytics")
    st.markdown("---")

    # API Key upload
    uploaded_key_file = st.file_uploader(
        "🔑 File API Key (.txt)",
        type=["txt", "text"],
        help="Tải lên file .txt chứa OpenAI API Key"
    )
    api_key = ""
    if uploaded_key_file is not None:
        try:
            api_key = uploaded_key_file.read().decode("utf-8").strip().split("\n")[0].strip()
            if api_key:
                os.environ["OPENAI_API_KEY"] = api_key
                st.success(f"🔑 Key đã nạp: {api_key[:8]}...{api_key[-4:]}")
        except Exception as e:
            st.error(f"Lỗi đọc file Key: {e}")
    else:
        api_key = os.getenv("OPENAI_API_KEY", "")
        if api_key:
            st.info(f"🔑 Dùng Key hệ thống: {api_key[:8]}...{api_key[-4:]}")

    model_choice = st.selectbox(
        "🤖 Model",
        ["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"],
        index=0,
    )
    os.environ["OPENAI_MODEL"] = model_choice

    st.markdown("---")
    st.markdown("**📁 Upload dữ liệu khảo sát**")

    # ── File 1: Export Survey (bắt buộc) ──
    uploaded = st.file_uploader(
        "📋 Export_Survey (bắt buộc)",
        type=["xlsx", "xls"],
        key="upload_export",
        help="File Export_Survey từ hệ thống khảo sát",
    )
    # ── File 2: DSSV (tuỳ chọn) ──
    uploaded_dssv = st.file_uploader(
        "👥 Danh sách SV (tuỳ chọn)",
        type=["xlsx", "xls"],
        key="upload_dssv",
        help="File DSSV để tính tỷ lệ phản hồi",
    )
    # ── File 3: Form template (tuỳ chọn) ──
    uploaded_form = st.file_uploader(
        "📄 Form Template (tuỳ chọn)",
        type=["xlsx", "xls"],
        key="upload_form",
        help="File Form.xlsx — mẫu báo cáo FPT",
    )

    # Auto-detect file có sẵn trong thư mục
    ROOT = Path(__file__).parent.parent
    default_file      = ROOT / "KS_Survey.xlsx"
    default_export    = next(ROOT.glob("Export_Survey*.xlsx"), None)
    default_dssv      = next(ROOT.glob("DSSV*.xlsx"), None)
    default_form      = ROOT / "Form.xlsx" if (ROOT / "Form.xlsx").exists() else None

    use_default = False
    if default_file.exists() and not uploaded:
        if st.button("📂 Dùng file mẫu KS_Survey.xlsx", use_container_width=True):
            use_default = True

    # Lưu đường dẫn file vào session state để Tab 7 (HTML) dùng
    def _save_upload(f, key):
        if f:
            p = Path("/tmp") / f.name
            p.write_bytes(f.getbuffer())
            st.session_state[key] = str(p)
        elif key not in st.session_state:
            st.session_state[key] = None

    _save_upload(uploaded_dssv, "path_dssv")
    _save_upload(uploaded_form, "path_form")
    if uploaded_form is None and default_form:
        st.session_state.setdefault("path_form", str(default_form))
    if uploaded_dssv is None and default_dssv:
        st.session_state.setdefault("path_dssv", str(default_dssv))

    st.markdown("---")
    st.markdown("""
    **📋 Hướng dẫn:**
    1. Nhập OpenAI API Key
    2. Upload file Export_Survey
    3. Nhấn **Phân tích ngay**
    4. Tab **📊 Báo cáo Chuẩn** — dùng tool HTML đầy đủ
    5. Tab **🤖 Phân tích Góp ý** — AI gom nhóm ý kiến
    """)
    st.markdown("---")
    st.markdown("<small style='color:#64748b;font-weight:600'>v2.1 - QA FECT</small>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# MAIN CONTENT
# ══════════════════════════════════════════════════════════════
st.markdown("# 🎓 AI Survey Analytics Dashboard")
st.markdown("<p style='color:#475569;margin-top:-10px'>Phân tích khảo sát sinh viên thông minh với AI · Insight · Cảm xúc · Cảnh báo</p>", unsafe_allow_html=True)
st.markdown("---")

# ── Determine file path ───────────────────────────────────────
filepath = None
if uploaded:
    tmp_path = Path("/tmp") / uploaded.name
    with open(tmp_path, "wb") as f:
        f.write(uploaded.getbuffer())
    filepath = str(tmp_path)
elif use_default or (default_file.exists() and "result" in st.session_state):
    filepath = str(default_file)

# ── Run analysis button ───────────────────────────────────────
if filepath and not ("result" in st.session_state and st.session_state.get("analyzed_file") == filepath):
    if not api_key:
        st.warning("⚠️ Vui lòng nhập OpenAI API Key trong thanh bên trái.")
    else:
        col_btn, _ = st.columns([1, 3])
        with col_btn:
            if st.button("🚀 Phân tích ngay", type="primary", use_container_width=True):
                progress_bar  = st.progress(0, text="Đang khởi động...")
                status_text   = st.empty()

                def progress_cb(msg, pct):
                    if pct is not None:
                        progress_bar.progress(pct / 100, text=msg)
                    status_text.markdown(f"*{msg}*")

                from src.pipeline.orchestrator import run_full_analysis
                try:
                    result = run_full_analysis(filepath, progress_callback=progress_cb)
                    st.session_state["result"]        = result
                    st.session_state["analyzed_file"] = filepath
                    progress_bar.progress(1.0, text="✅ Hoàn tất!")
                    status_text.empty()
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Lỗi phân tích: {e}")
                    st.stop()

elif not filepath:
    # Hero landing
    st.markdown("""
    <div style="text-align:center; padding: 60px 0;">
      <div style="font-size:5rem; margin-bottom:16px;">🎓</div>
      <h2 style="color:#a78bfa; font-weight:700;">Bắt đầu phân tích khảo sát</h2>
      <p style="color:rgba(255,255,255,0.6); max-width:500px; margin:0 auto; line-height:1.7;">
        Upload file Excel khảo sát sinh viên và nhận ngay báo cáo AI đầy đủ:<br>
        Phân tích cảm xúc · Insight · Điểm mạnh/nghẽn · Checklist cảnh báo
      </p>
    </div>
    """, unsafe_allow_html=True)

    # Feature cards
    c1, c2, c3, c4 = st.columns(4)
    for col, icon, title, desc in [
        (c1, "💬", "Sentiment AI", "Phân loại cảm xúc từng phản hồi mở"),
        (c2, "🔍", "Insight Extraction", "Bóc tách chủ đề, xu hướng quan trọng"),
        (c3, "💪", "Điểm mạnh/nghẽn", "Nhận diện tự động dựa trên dữ liệu"),
        (c4, "⚠️", "Alert & Checklist", "Cảnh báo KPI vượt ngưỡng"),
    ]:
        with col:
            st.markdown(f"""<div class='metric-card'>
                <div style='font-size:2rem'>{icon}</div>
                <div style='font-weight:700;color:#ff6b00;margin:8px 0 4px'>{title}</div>
                <div style='font-size:0.82rem;color:#475569'>{desc}</div>
            </div>""", unsafe_allow_html=True)
    st.stop()


# ══════════════════════════════════════════════════════════════
# RESULT DISPLAY
# ══════════════════════════════════════════════════════════════
if "result" not in st.session_state:
    st.stop()

R   = st.session_state["result"]
df  = R["df"]
stats           = R["stats"]
sentiment_sum   = R["sentiment_summary"]
all_insights    = R["all_insights"]
exec_sum        = R["executive_summary"]
strengths       = R["strengths"]
bottlenecks     = R["bottlenecks"]
watch_list      = R["watch_list"]
q_stats         = R["question_stats"]
checklist       = R["checklist"]
actions         = R["actions"]
comments_df     = R["comments_df"]


# ══ KPI CARDS ════════════════════════════════════════════════
c1, c2, c3, c4, c5 = st.columns(5)
avg_score = stats["avg_satisfaction"]
total     = stats["total"]
pos_total = sum(v["positive"] for v in sentiment_sum.values())
neg_total = sum(v["negative"] for v in sentiment_sum.values())
all_total = sum(v["total"]    for v in sentiment_sum.values())

kpis = [
    (c1, str(total),                               "Tổng phản hồi"),
    (c2, f"{avg_score:.2f}/5",                     "Điểm hài lòng TB"),
    (c3, f"{pos_total/all_total*100:.1f}%" if all_total else "N/A", "Tỷ lệ tích cực"),
    (c4, f"{len(strengths)}",                      "Điểm mạnh"),
    (c5, f"{len(bottlenecks)}",                    "Điểm nghẽn"),
]
for col, num, label in kpis:
    with col:
        st.markdown(f"""<div class='metric-card'>
            <div class='metric-number'>{num}</div>
            <div class='metric-label'>{label}</div>
        </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ══ TABS ═════════════════════════════════════════════════════
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "📋 Tổng quan",
    "💬 Cảm xúc",
    "🔍 Insight",
    "💪 Điểm mạnh / Nghẽn",
    "✅ Checklist & Cảnh báo",
    "💡 Đề xuất hành động",
    "📊 Báo cáo & Phân tích Góp ý",
])


# ═══════════════════════════════════════════════════════════
# TAB 1: TỔNG QUAN
# ═══════════════════════════════════════════════════════════
with tab1:
    # Executive Summary
    st.markdown(f"""<div class='exec-card'>
        <div class='exec-headline'>📌 {exec_sum.get('headline', 'Kết quả Khảo Sát Sinh Viên')}</div>
        <div class='exec-overview'>{exec_sum.get('overview', '')}</div>
    </div>""", unsafe_allow_html=True)

    # Top insights
    top_insights = exec_sum.get("top_insights", [])
    if top_insights:
        st.markdown("<div class='section-header'>🏆 Top Insight Quan Trọng</div>", unsafe_allow_html=True)
        for ins in top_insights:
            impact_color = {"high": "#ef4444", "medium": "#f59e0b", "low": "#10b981"}.get(ins.get("impact","low"), "#2563eb")
            st.markdown(f"""
            <div style='background:rgba(0,0,0,0.03);border-radius:10px;padding:14px 18px;
                        margin-bottom:10px;border-left:4px solid {impact_color}'>
                <span style='color:{impact_color};font-weight:700'>#{ins.get('rank','')}</span>
                <span style='color:#0f172a;margin-left:10px;font-weight:500'>{ins.get('insight','')}</span>
                <span style='float:right;font-size:0.75rem;color:#64748b;font-weight:600'>{ins.get('impact','').upper()}</span>
            </div>""", unsafe_allow_html=True)

    col_l, col_r = st.columns(2)

    with col_l:
        st.markdown("<div class='section-header'>📊 Phân bổ khối ngành</div>", unsafe_allow_html=True)
        major_data = pd.DataFrame(list(stats["majors"].items()), columns=["Ngành", "Số lượng"])
        fig_major = px.pie(
            major_data, values="Số lượng", names="Ngành",
            color_discrete_sequence=["#a78bfa", "#60a5fa", "#34d399"],
            hole=0.45,
        )
        fig_major.update_layout(**PLOTLY_LAYOUT, showlegend=True,
                                 legend=dict(font=dict(color="#0f172a")))
        fig_major.update_traces(textfont_color="white", textfont_size=13)
        st.plotly_chart(fig_major, use_container_width=True)

    with col_r:
        st.markdown("<div class='section-header'>📈 Điểm trung bình theo tiêu chí</div>", unsafe_allow_html=True)
        q_labels = [v for v in QUESTION_MAP.values()]
        q_avgs   = [q_stats[q]["avg"] if q in q_stats else 0 for q in QUESTION_MAP]
        colors   = ["#10b981" if s >= 4.2 else "#f59e0b" if s >= 3.8 else "#ef4444" for s in q_avgs]

        fig_bar = go.Figure(go.Bar(
            x=q_labels, y=q_avgs,
            marker_color=colors,
            text=[f"{v:.2f}" for v in q_avgs],
            textposition="outside",
            textfont=dict(color="#0f172a", size=12),
        ))
        fig_bar.update_layout(
            **PLOTLY_LAYOUT,
            yaxis=dict(range=[0, 5.5], gridcolor="#e2e8f0"),
            xaxis=dict(tickangle=-30),
        )
        st.plotly_chart(fig_bar, use_container_width=True)


# ═══════════════════════════════════════════════════════════
# TAB 2: CẢM XÚC
# ═══════════════════════════════════════════════════════════
with tab2:
    st.markdown("<div class='section-header'>💬 Phân tích cảm xúc theo từng tiêu chí</div>", unsafe_allow_html=True)

    # Stacked bar chart
    q_labels_short = [QUESTION_MAP[q] for q in QUESTION_MAP if q in sentiment_sum]
    pos_vals = [sentiment_sum[q]["pos_pct"]  for q in QUESTION_MAP if q in sentiment_sum]
    neg_vals = [sentiment_sum[q]["neg_pct"]  for q in QUESTION_MAP if q in sentiment_sum]
    neu_vals = [100 - p - n for p, n in zip(pos_vals, neg_vals)]

    fig_sent = go.Figure()
    fig_sent.add_trace(go.Bar(name="✅ Tích cực", x=q_labels_short, y=pos_vals,
                               marker_color="#34d399", text=[f"{v:.0f}%" for v in pos_vals],
                               textposition="inside", textfont=dict(color="white", size=11)))
    fig_sent.add_trace(go.Bar(name="➖ Trung tính", x=q_labels_short, y=neu_vals,
                               marker_color="#60a5fa", text=[f"{v:.0f}%" for v in neu_vals],
                               textposition="inside", textfont=dict(color="white", size=11)))
    fig_sent.add_trace(go.Bar(name="❌ Tiêu cực", x=q_labels_short, y=neg_vals,
                               marker_color="#f87171", text=[f"{v:.0f}%" for v in neg_vals],
                               textposition="inside", textfont=dict(color="white", size=11)))
    fig_sent.update_layout(**PLOTLY_LAYOUT, barmode="stack",
                            xaxis=dict(tickangle=-30),
                            yaxis=dict(title="Tỷ lệ %", gridcolor="#e2e8f0"),
                            legend=dict(font=dict(color="#0f172a")))
    st.plotly_chart(fig_sent, use_container_width=True)

    # Radar chart
    col_r1, col_r2 = st.columns(2)
    with col_r1:
        st.markdown("<div class='section-header'>🕸️ Radar điểm hài lòng</div>", unsafe_allow_html=True)
        avgs = [q_stats[q]["avg"] if q in q_stats else 0 for q in QUESTION_MAP]
        labels = list(QUESTION_MAP.values())
        fig_radar = go.Figure(go.Scatterpolar(
            r=avgs + [avgs[0]],
            theta=labels + [labels[0]],
            fill="toself",
            fillcolor="rgba(167,139,250,0.2)",
            line=dict(color="#a78bfa", width=2),
            marker=dict(color="#a78bfa", size=6),
        ))
        fig_radar.update_layout(
            **PLOTLY_LAYOUT,
            polar=dict(
                bgcolor="rgba(0,0,0,0)",
                radialaxis=dict(visible=True, range=[0, 5],
                                gridcolor="#e2e8f0",
                                tickfont=dict(color="#475569", size=9)),
                angularaxis=dict(tickfont=dict(color="#0f172a", size=10)),
            ),
        )
        st.plotly_chart(fig_radar, use_container_width=True)

    with col_r2:
        st.markdown("<div class='section-header'>📝 Phản hồi mở có cảm xúc</div>", unsafe_allow_html=True)
        ai_df = comments_df[comments_df["Comment"].notna() & comments_df["AI_Sentiment"].notna()]
        if len(ai_df) > 0:
            # Pie cảm xúc AI
            sent_vc = ai_df["AI_Sentiment"].value_counts()
            fig_ai = px.pie(
                values=sent_vc.values,
                names=sent_vc.index,
                color=sent_vc.index,
                color_discrete_map=CHART_COLORS,
                hole=0.5,
            )
            fig_ai.update_layout(**PLOTLY_LAYOUT, showlegend=True,
                                  legend=dict(font=dict(color="#0f172a")))
            fig_ai.update_traces(textfont_color="white")
            st.plotly_chart(fig_ai, use_container_width=True)
        else:
            st.info("Không có đủ phản hồi mở để phân tích AI Sentiment.")

    # Comment table
    st.markdown("<div class='section-header'>💬 Mẫu phản hồi mở</div>", unsafe_allow_html=True)
    filter_sent = st.selectbox("Lọc cảm xúc:", ["Tất cả", "positive", "negative", "neutral"])
    disp_df = comments_df[comments_df["Comment"].notna()].copy()
    if filter_sent != "Tất cả":
        disp_df = disp_df[disp_df["AI_Sentiment"] == filter_sent]

    disp_df["Cảm xúc"] = disp_df["AI_Sentiment"].map(
        {"positive": "✅ Tích cực", "negative": "❌ Tiêu cực", "neutral": "➖ Trung tính"}
    ).fillna("—")

    st.dataframe(
        disp_df[["QLabel", "Comment", "Cảm xúc", "AI_Emotion", "Major"]].head(30)
            .rename(columns={"QLabel": "Tiêu chí", "Comment": "Phản hồi",
                             "AI_Emotion": "Cảm xúc chi tiết", "Major": "Ngành"}),
        use_container_width=True, hide_index=True,
    )


# ═══════════════════════════════════════════════════════════
# TAB 3: INSIGHT
# ═══════════════════════════════════════════════════════════
with tab3:
    st.markdown("<div class='section-header'>🔍 Insight chi tiết theo từng tiêu chí</div>", unsafe_allow_html=True)

    selected_q = st.selectbox(
        "Chọn tiêu chí:",
        options=list(QUESTION_MAP.keys()),
        format_func=lambda k: f"{k} — {QUESTION_MAP[k]}",
    )

    ins = all_insights.get(selected_q, {})

    col_i1, col_i2 = st.columns([2, 1])
    with col_i1:
        st.markdown(f"""<div class='exec-card'>
            <div style='font-size:1rem;font-weight:700;color:#ff6b00;margin-bottom:8px'>
                📌 Tóm tắt: {QUESTION_MAP[selected_q]}
            </div>
            <div style='color:#334155;line-height:1.7;font-weight:500'>
                {ins.get('summary', 'Không có dữ liệu')}
            </div>
        </div>""", unsafe_allow_html=True)

        # Topics
        topics = ins.get("topics", [])
        if topics:
            st.markdown("**📂 Các chủ đề nổi bật:**")
            topic_df = pd.DataFrame(topics)
            if "topic" in topic_df.columns and "count" in topic_df.columns:
                color_map = {"positive": "#10b981", "negative": "#ef4444", "neutral": "#3b82f6"}
                topic_df["color"] = topic_df.get("sentiment", "neutral").map(color_map) if "sentiment" in topic_df.columns else "#3b82f6"
                fig_topics = px.bar(
                    topic_df.sort_values("count", ascending=True).tail(8),
                    x="count", y="topic", orientation="h",
                    color="count", color_continuous_scale=["#ff6b00", "#ffb900"],
                )
                fig_topics.update_layout(**PLOTLY_LAYOUT,
                                         xaxis=dict(gridcolor="#e2e8f0"),
                                         coloraxis_showscale=False)
                st.plotly_chart(fig_topics, use_container_width=True)

    with col_i2:
        pos_themes = ins.get("positive_themes", [])
        neg_themes = ins.get("negative_themes", [])

        if pos_themes:
            st.markdown("**✅ Điểm được đánh giá tốt:**")
            for t in pos_themes:
                st.markdown(f"<div class='strength-item'>👍 {t}</div>", unsafe_allow_html=True)

        if neg_themes:
            st.markdown("**❌ Vấn đề được phản ánh:**")
            for t in neg_themes:
                st.markdown(f"<div class='bottleneck-item'>⚠️ {t}</div>", unsafe_allow_html=True)

        recs = ins.get("recommendations", [])
        if recs:
            st.markdown("**💡 Đề xuất:**")
            for r in recs:
                st.markdown(f"<div class='watch-item'>→ {r}</div>", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════
# TAB 4: ĐIỂM MẠNH / NGHẼN
# ═══════════════════════════════════════════════════════════
with tab4:
    col_s, col_b = st.columns(2)

    with col_s:
        st.markdown(f"<div class='section-header'>💪 Điểm mạnh ({len(strengths)})</div>", unsafe_allow_html=True)
        if strengths:
            for s in strengths:
                st.markdown(f"""<div class='strength-item'>
                    <b>{s['label']}</b><br>
                    <small>⭐ {s['avg']}/5 · ✅ {s['pos_rate']}% tích cực</small>
                </div>""", unsafe_allow_html=True)
        else:
            st.info("Không có tiêu chí nào đạt ngưỡng Điểm mạnh.")

    with col_b:
        st.markdown(f"<div class='section-header'>🔴 Điểm nghẽn ({len(bottlenecks)})</div>", unsafe_allow_html=True)
        if bottlenecks:
            for b in bottlenecks:
                st.markdown(f"""<div class='bottleneck-item'>
                    <b>{b['label']}</b><br>
                    <small>⭐ {b['avg']}/5 · ❌ {b['neg_rate']}% tiêu cực</small>
                </div>""", unsafe_allow_html=True)
        else:
            st.success("Không phát hiện điểm nghẽn đáng kể. 🎉")

    if watch_list:
        st.markdown(f"<div class='section-header'>⚠️ Cần theo dõi ({len(watch_list)})</div>", unsafe_allow_html=True)
        for w in watch_list:
            st.markdown(f"""<div class='watch-item'>
                <b>{w['label']}</b> · ⭐ {w['avg']}/5 · Tiêu cực: {w['neg_rate']}%
            </div>""", unsafe_allow_html=True)





# ═══════════════════════════════════════════════════════════
# TAB 5: CHECKLIST & ALERT
# ═══════════════════════════════════════════════════════════
with tab5:
    st.markdown("<div class='section-header'>✅ Checklist Theo Dõi KPI</div>", unsafe_allow_html=True)

    # Alert summary
    critical_items = [c for c in checklist if c["status"] == "critical"]
    warning_items  = [c for c in checklist if c["status"] == "warning"]
    ok_items       = [c for c in checklist if c["status"] == "ok"]

    ca, cw, co = st.columns(3)
    with ca:
        st.markdown(f"""<div class='metric-card' style='border-color:rgba(248,113,113,0.4)'>
            <div class='metric-number' style='background:linear-gradient(135deg,#f87171,#dc2626);-webkit-background-clip:text'>
                {len(critical_items)}
            </div>
            <div class='metric-label'>🔴 Critical</div>
        </div>""", unsafe_allow_html=True)
    with cw:
        st.markdown(f"""<div class='metric-card' style='border-color:rgba(251,191,36,0.4)'>
            <div class='metric-number' style='background:linear-gradient(135deg,#fbbf24,#d97706);-webkit-background-clip:text'>
                {len(warning_items)}
            </div>
            <div class='metric-label'>⚠️ Warning</div>
        </div>""", unsafe_allow_html=True)
    with co:
        st.markdown(f"""<div class='metric-card' style='border-color:rgba(52,211,153,0.4)'>
            <div class='metric-number' style='background:linear-gradient(135deg,#34d399,#059669);-webkit-background-clip:text'>
                {len(ok_items)}
            </div>
            <div class='metric-label'>✅ Bình thường</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Checklist table
    for item in checklist:
        status_style = {
            "critical": "checklist-critical",
            "warning":  "checklist-warning",
            "ok":       "checklist-ok",
        }.get(item["status"], "checklist-ok")

        border_color = {"critical": "#f87171", "warning": "#fbbf24", "ok": "#34d399"}.get(item["status"], "#60a5fa")
        bg_color     = {"critical": "rgba(248,113,113,0.08)", "warning": "rgba(251,191,36,0.06)", "ok": "rgba(52,211,153,0.06)"}.get(item["status"], "transparent")

        st.markdown(f"""
        <div style='background:{bg_color};border:1px solid {border_color};border-radius:12px;
                    padding:18px 22px;margin-bottom:12px;display:flex;align-items:center;gap:20px;flex-wrap:wrap'>
            <div style='font-size:1.6rem'>{item['icon']}</div>
            <div style='flex:1;min-width:200px'>
                <div style='font-weight:700;color:#0f172a;font-size:1rem'>{item['group']}</div>
                <div style='color:#475569;font-size:0.82rem;margin-top:2px'>{item['kpi_name']}</div>
            </div>
            <div style='text-align:center;min-width:80px'>
                <div style='font-size:1.4rem;font-weight:800;color:#0f172a'>
                    {item['kpi_value']}{item['unit']}
                </div>
                <div style='font-size:0.75rem;color:#64748b'>Giá trị hiện tại</div>
            </div>
            <div style='text-align:right;min-width:220px'>
                <div class='{status_style}' style='font-size:1rem'>{item['status_icon']} {item['alert']}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Gauge charts
    st.markdown("<div class='section-header'>🎯 Gauge KPI</div>", unsafe_allow_html=True)
    gauge_cols = st.columns(len(checklist))
    for i, (col, item) in enumerate(zip(gauge_cols, checklist)):
        with col:
            max_val   = 5   if item["unit"] == "/5" else 100
            threshold = 3.5 if item["unit"] == "/5" else 25
            color     = {"ok": "#34d399", "warning": "#fbbf24", "critical": "#f87171"}.get(item["status"], "#60a5fa")
            fig_g = go.Figure(go.Indicator(
                mode="gauge+number",
                value=item["kpi_value"],
                title={"text": item["group"][:20], "font": {"size": 11, "color": "#0f172a"}},
                gauge={
                    "axis": {"range": [0, max_val], "tickcolor": "#0f172a"},
                    "bar":  {"color": color},
                    "bgcolor": "rgba(0,0,0,0.05)",
                    "bordercolor": "rgba(0,0,0,0.1)",
                    "steps": [
                        {"range": [0, threshold * 0.7], "color": "rgba(52,211,153,0.15)"},
                        {"range": [threshold * 0.7, threshold], "color": "rgba(251,191,36,0.15)"},
                        {"range": [threshold, max_val], "color": "rgba(248,113,113,0.15)"},
                    ],
                },
                number={"font": {"color": color, "size": 22}, "suffix": item["unit"]},
            ))
            gauge_layout = {**PLOTLY_LAYOUT, "height": 200, "margin": dict(t=50, b=10, l=20, r=20)}
            fig_g.update_layout(**gauge_layout)
            st.plotly_chart(fig_g, use_container_width=True)


# ═══════════════════════════════════════════════════════════
# TAB 6: ĐỀ XUẤT HÀNH ĐỘNG
# ═══════════════════════════════════════════════════════════
with tab6:
    st.markdown("<div class='section-header'>💡 Đề xuất Hành động Ưu tiên</div>", unsafe_allow_html=True)

    if exec_sum.get("key_action"):
        st.markdown(f"""<div class='exec-card'>
            <div style='font-size:0.85rem;color:#ff6b00;font-weight:600;margin-bottom:6px'>🎯 HÀNH ĐỘNG ƯU TIÊN CAO NHẤT</div>
            <div style='color:#0f172a;font-size:1.05rem;font-weight:600'>{exec_sum['key_action']}</div>
        </div>""", unsafe_allow_html=True)

    if actions:
        priority_order = {"high": 0, "medium": 1, "low": 2}
        sorted_actions = sorted(actions, key=lambda x: priority_order.get(x.get("priority","low"), 2))

        for act in sorted_actions:
            priority  = act.get("priority", "medium")
            p_color   = {"high": "#ef4444", "medium": "#f59e0b", "low": "#10b981"}.get(priority, "#2563eb")
            p_label   = {"high": "🔴 Cao", "medium": "🟡 Trung bình", "low": "🟢 Thấp"}.get(priority, "")
            css_class = f"action-{priority} action-card"

            st.markdown(f"""<div class='{css_class}'>
                <div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:6px'>
                    <span style='font-weight:700;color:#0f172a'>{act.get('action','')}</span>
                    <span style='font-size:0.8rem;color:{p_color};font-weight:600'>{p_label}</span>
                </div>
                <div style='display:flex;gap:16px;font-size:0.82rem;color:#475569'>
                    <span>📂 {act.get('category','')}</span>
                    <span>⏱️ {act.get('timeline','')}</span>
                    <span>🎯 {act.get('expected_impact','')}</span>
                </div>
            </div>""", unsafe_allow_html=True)
    else:
        st.info("Không có đề xuất hành động nào được tạo.")

    # Download data
    st.markdown("<div class='section-header'>📥 Tải xuống dữ liệu</div>", unsafe_allow_html=True)
    col_d1, col_d2 = st.columns(2)

    with col_d1:
        csv_data = df.to_csv(index=False, encoding="utf-8-sig")
        st.download_button(
            "📊 Tải dữ liệu đã xử lý (CSV)",
            csv_data.encode("utf-8-sig"),
            "survey_processed.csv", "text/csv",
            use_container_width=True,
        )

    with col_d2:
        if len(comments_df) > 0:
            comments_csv = comments_df[comments_df["Comment"].notna()].to_csv(index=False, encoding="utf-8-sig")
            st.download_button(
                "💬 Tải phân tích phản hồi mở (CSV)",
                comments_csv.encode("utf-8-sig"),
                "comments_analysis.csv", "text/csv",
                use_container_width=True,
            )


# ═══════════════════════════════════════════════════════════════
# TAB 7: BÁO CÁO CHUẨN & PHÂN TÍCH GÓP Ý AI
# ═══════════════════════════════════════════════════════════════
with tab7:
    st.markdown("<div class='section-header'>📊 Xuất Báo Cáo & Phân Tích Góp Ý AI</div>",
                unsafe_allow_html=True)
    st.markdown("""
    <div style='background:rgba(255,107,0,0.04);border-radius:12px;padding:14px 20px;
                border:1px solid rgba(255,107,0,0.15);margin-bottom:16px;font-size:0.88rem;
                color:#334155;line-height:1.7'>
        📌 <b>Tính năng:</b> Điền tự động các chỉ số khảo sát vào mẫu báo cáo chuẩn FPT (<code>Form.xlsx</code>). 
        Nếu bạn chạy <b>phân tích gom nhóm ý kiến bằng AI</b> ở phần bên dưới, báo cáo tải về sẽ <b>tự động đính kèm thêm sheet "GOM NHÓM Ý KIẾN (AI)"</b>.
    </div>
    """, unsafe_allow_html=True)

    if "result" not in st.session_state:
        st.info("⚠️ Vui lòng chạy phân tích dữ liệu khảo sát ở tab Tổng quan trước.")
    else:
        # ── PHẦN 1: CẤU HÌNH & XUẤT EXCEL ──
        st.markdown("<div class='section-header'>⚙️ 1. Cấu hình & Xuất báo cáo Excel FPT</div>",
                    unsafe_allow_html=True)
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            ky_input = st.text_input("Kỳ học", value="Spring 2026")
        with col_c2:
            coso_input = st.text_input("Cơ sở", value="FPTU Cần Thơ")

        template_file = Path(__file__).parent.parent / "Form.xlsx"
        uploaded_template = st.file_uploader(
            "📁 Tải lên Form Template (.xlsx) khác nếu muốn thay đổi mẫu",
            type=["xlsx"],
            key="upload_custom_template"
        )
        
        final_template_path = None
        if uploaded_template:
            temp_template_path = Path("/tmp") / uploaded_template.name
            temp_template_path.write_bytes(uploaded_template.getbuffer())
            final_template_path = str(temp_template_path)
            st.success(f"✅ Đã nhận mẫu tải lên: {uploaded_template.name}")
        elif template_file.exists():
            final_template_path = str(template_file)
            st.success("✅ Đã tìm thấy mẫu báo cáo mặc định Form.xlsx trong thư mục dự án.")
        else:
            st.warning("⚠️ Không tìm thấy mẫu mặc định Form.xlsx. Vui lòng tải file mẫu lên:")
            
        if final_template_path:
            dssv_path = st.session_state.get("path_dssv")
            dssv_df = None
            if dssv_path and Path(dssv_path).exists():
                try:
                    dssv_df = pd.read_excel(dssv_path)
                    st.info(f"👥 Sử dụng danh sách sinh viên: {Path(dssv_path).name} để tính tỷ lệ phản hồi.")
                except Exception as e:
                    st.error(f"Lỗi đọc danh sách sinh viên: {e}")

            # Note đính kèm AI kết quả
            if "ai_group_result" in st.session_state:
                st.markdown("""
                <div style='background:rgba(52,211,153,0.08);color:#34d399;border:1px solid rgba(52,211,153,0.2);
                            border-radius:8px;padding:8px 12px;font-size:0.82rem;margin-bottom:10px'>
                    ✨ <b>Sẵn sàng:</b> Kết quả gom nhóm của <b>AI</b> sẽ được tự động chèn thành sheet riêng trong file Excel báo cáo.
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style='background:rgba(251,146,60,0.08);color:#fb923c;border:1px solid rgba(251,146,60,0.2);
                            border-radius:8px;padding:8px 12px;font-size:0.82rem;margin-bottom:10px'>
                    💡 <b>Mẹo:</b> Bạn có thể kéo xuống phần 2 chạy gom nhóm ý kiến đóng góp bằng AI trước để file báo cáo Excel xuất ra đầy đủ hơn.
                </div>
                """, unsafe_allow_html=True)

            if st.button("🚀 Xuất báo cáo Excel FPT", type="primary", use_container_width=True):
                from src.report.excel_generator import fill_fpt_template
                try:
                    out_name = f"TongHop_BaoCaoKSSV_{coso_input.replace(' ', '')}_{ky_input.replace(' ', '')}.xlsx"
                    output_file_path = fill_fpt_template(
                        survey_df=st.session_state["result"]["df"],
                        dssv_df=dssv_df,
                        template_path=final_template_path,
                        output_path=out_name,
                        ky=ky_input,
                        coso=coso_input,
                        ai_group_result=st.session_state.get("ai_group_result")
                    )
                    
                    with open(output_file_path, "rb") as f:
                        st.download_button(
                            "📥 Tải xuống Báo cáo Excel FPT hoàn thành",
                            f.read(),
                            out_name,
                            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            use_container_width=True
                        )
                    st.success("✅ Điền dữ liệu vào mẫu thành công! Bấm nút phía trên để tải về.")
                except Exception as e:
                    st.error(f"Lỗi khi xuất báo cáo: {e}")

        # ── PHẦN 2: PHÂN TÍCH GÓP Ý AI ──
        st.markdown("<br><hr><br>", unsafe_allow_html=True)
        st.markdown("<div class='section-header'>🤖 2. Phân tích & Gom nhóm ý kiến bằng AI</div>",
                    unsafe_allow_html=True)

        valid_comments = comments_df[comments_df["Comment"].notna()].copy()
        
        # Build feedback list giống KS_Survey.html
        SKIP_WORDS = {"ko có", "ko co", "không có", "khong co", "ok", "oke", "n/a", "na",
                      "không", "khong", ".", "q", "k", "ko", "binh thuong"}
        feedbacks = []
        for _, row in valid_comments.iterrows():
            content = (row["Comment"] or "").strip()
            if len(content) > 5 and content.lower() not in SKIP_WORDS:
                feedbacks.append({
                    "stt":      len(feedbacks) + 1,
                    "question": f"Câu {row['Question'][1:]}",  # Q1 → Câu 1
                    "content":  content,
                    "major":    row.get("Major", "N/A"),
                })

        if len(feedbacks) == 0:
            st.info("Không có ý kiến đóng góp hợp lệ nào để phân tích.")
        else:
            # Stats row
            c_f1, c_f2, c_f3 = st.columns(3)
            with c_f1:
                st.markdown(f"""<div class='metric-card'>
                    <div class='metric-number'>{len(feedbacks)}</div>
                    <div class='metric-label'>Tổng góp ý hợp lệ</div>
                </div>""", unsafe_allow_html=True)
            with c_f2:
                q_counts = pd.Series([fb["question"] for fb in feedbacks]).value_counts()
                most_q = q_counts.index[0] if len(q_counts) > 0 else "N/A"
                st.markdown(f"""<div class='metric-card'>
                    <div class='metric-number'>{most_q}</div>
                    <div class='metric-label'>Câu nhiều góp ý nhất</div>
                </div>""", unsafe_allow_html=True)
            with c_f3:
                majors_in_fb = pd.Series([fb["major"] for fb in feedbacks]).nunique()
                st.markdown(f"""<div class='metric-card'>
                    <div class='metric-number'>{majors_in_fb}</div>
                    <div class='metric-label'>Số ngành có góp ý</div>
                </div>""", unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # Bảng góp ý thô
            with st.expander(f"📋 Xem {len(feedbacks)} góp ý thô của sinh viên", expanded=False):
                fb_df = pd.DataFrame(feedbacks)
                st.dataframe(
                    fb_df[["stt", "question", "major", "content"]]
                        .rename(columns={"stt": "STT", "question": "Câu",
                                         "major": "Ngành", "content": "Nội dung góp ý"}),
                    use_container_width=True, hide_index=True,
                )

            st.markdown("<div class='section-header'>✨ Gom Nhóm & Tóm Tắt bằng AI</div>",
                        unsafe_allow_html=True)

            # Phân tích AI
            if not api_key:
                st.warning("⚠️ Vui lòng upload file chứa OpenAI API Key (.txt) trong sidebar để phân tích AI.")
            else:
                run_ai_btn = st.button(
                    "✨ Bắt đầu Phân tích & Gom nhóm AI",
                    type="primary",
                    key="btn_ai_group_combined",
                    use_container_width=True
                )

                if run_ai_btn or "ai_group_result" in st.session_state:
                    if run_ai_btn:  # Chạy mới
                        from src.agents.ai_agents import group_feedbacks
                        ai_status = st.empty()
                        prog = st.progress(0, text="Đang chuẩn bị...")

                        log_msgs = []
                        def ai_log(msg):
                            log_msgs.append(msg)
                            ai_status.markdown(f"*{msg}*")
                            prog.progress(min(len(log_msgs) * 15, 95), text=msg)

                        try:
                            result_ai = group_feedbacks(feedbacks, progress_callback=ai_log)
                            st.session_state["ai_group_result"] = result_ai
                            prog.progress(100, text="✅ Hoàn tất!")
                            ai_status.empty()
                            st.rerun()
                        except Exception as e:
                            prog.empty()
                            st.error(f"❌ Lỗi phân tích AI: {repr(e)}")

                    if "ai_group_result" in st.session_state:
                        ai_res = st.session_state["ai_group_result"]
                        groups = ai_res.get("groups", [])

                        # Hiển thị thống kê nhóm AI
                        sent_counts = {}
                        for g in groups:
                            s = g.get("sentiment", "neutral")
                            sent_counts[s] = sent_counts.get(s, 0) + g.get("count", 0)

                        s1, s2, s3, s4, s5 = st.columns(5)
                        for col, key, label, color in [
                            (s1, None,         f"{len(groups)} Nhóm",         "#a78bfa"),
                            (s2, None,         f"{ai_res.get('total_feedbacks', len(feedbacks))} Ý kiến", "#60a5fa"),
                            (s3, "positive",   f"{sent_counts.get('positive',0)} Tích cực",  "#34d399"),
                            (s4, "negative",   f"{sent_counts.get('negative',0)} Tiêu cực",  "#f87171"),
                            (s5, "suggestion", f"{sent_counts.get('suggestion',0)} Đề xuất", "#fb923c"),
                        ]:
                            with col:
                                val, lbl = label.split(" ", 1)
                                st.markdown(f"""<div class='metric-card' style='border-color:{color}33'>
                                    <div class='metric-number' style='background:{color};-webkit-background-clip:text'>{val}</div>
                                    <div class='metric-label'>{lbl}</div>
                                </div>""", unsafe_allow_html=True)

                        st.markdown(f"<small style='color:rgba(255,255,255,0.4)'>Model đã dùng: {ai_res.get('model_used','')}</small>",
                                    unsafe_allow_html=True)
                        st.markdown("<br>", unsafe_allow_html=True)

                        # Hiển thị các nhóm ý kiến
                        sent_order = {"negative": 0, "suggestion": 1, "neutral": 2, "positive": 3}
                        sorted_groups = sorted(groups,
                            key=lambda g: (sent_order.get(g.get("sentiment","neutral"), 2), -g.get("count", 0)))

                        sent_emoji = {"positive": "😊", "negative": "😟", "neutral": "😐", "suggestion": "💡"}
                        sent_label = {"positive": "Tích cực", "negative": "Tiêu cực",
                                      "neutral": "Trung lập", "suggestion": "Đề xuất"}
                        sent_color = {"positive": "#34d399", "negative": "#f87171",
                                      "neutral":  "#9ca3af",  "suggestion": "#fb923c"}

                        for gi, group in enumerate(sorted_groups):
                            sent     = group.get("sentiment", "neutral")
                            em       = sent_emoji.get(sent, "📝")
                            lbl_s    = sent_label.get(sent, sent)
                            clr      = sent_color.get(sent, "#60a5fa")

                            with st.expander(
                                f"{em} {group.get('name','Nhóm ' + str(gi+1))}  ·  "
                                f"{group.get('count',0)} ý kiến  ·  {lbl_s}  ·  {group.get('question_scope','')}",
                                expanded=(sent == "negative"),
                            ):
                                st.markdown(f"""
                                <div style='background:rgba(245,158,11,0.08);border-left:4px solid #f59e0b;
                                            border-radius:8px;padding:12px 16px;margin-bottom:12px'>
                                    <div style='font-size:0.75rem;font-weight:700;color:#d97706;
                                                text-transform:uppercase;letter-spacing:0.5px;margin-bottom:6px'>
                                        ✍️ Tóm tắt chuyên gia
                                    </div>
                                    <div style='color:#1e293b;line-height:1.65;font-size:0.9rem'>
                                        {group.get('summary','')}
                                    </div>
                                </div>""", unsafe_allow_html=True)

                                resp = group.get("suggested_response", "")
                                if resp:
                                    st.markdown(f"""
                                    <div style='background:rgba(16,185,129,0.08);border-left:4px solid #10b981;
                                                border-radius:8px;padding:12px 16px;margin-bottom:12px'>
                                        <div style='font-size:0.75rem;font-weight:700;color:#047857;
                                                    text-transform:uppercase;letter-spacing:0.5px;margin-bottom:6px'>
                                            💬 Gợi ý phản hồi từ nhà trường
                                        </div>
                                        <div style='color:#065f46;line-height:1.65;font-size:0.9rem'>
                                            {resp}
                                        </div>
                                    </div>""", unsafe_allow_html=True)

                                originals = group.get("originals", [])
                                if originals:
                                    st.markdown(f"<div style='font-size:0.75rem;color:#64748b;margin-bottom:6px'>📋 Ý kiến gốc ({len(originals)})</div>",
                                                unsafe_allow_html=True)
                                    for fb in originals:
                                        st.markdown(f"""
                                        <div style='display:flex;gap:10px;padding:8px 12px;
                                                    border-bottom:1px solid #e2e8f0;font-size:0.85rem'>
                                            <span style='background:rgba(255,107,0,0.1);color:#d97706;
                                                         border-radius:12px;padding:2px 10px;white-space:nowrap;
                                                         font-size:0.75rem;font-weight:600;flex-shrink:0;
                                                         height:fit-content;margin-top:2px'>
                                                {fb.get('question','')} · {fb.get('major','')}
                                            </span>
                                            <span style='color:#334155;line-height:1.55'>{fb.get('content','')}</span>
                                        </div>""", unsafe_allow_html=True)

                        # CSV Download button for grouped feedbacks
                        st.markdown("<br>", unsafe_allow_html=True)
                        rows_export = []
                        for g in sorted_groups:
                            for fb in g.get("originals", []):
                                rows_export.append({
                                    "Nhóm":             g.get("name", ""),
                                    "Sentiment":        sent_label.get(g.get("sentiment",""), ""),
                                    "Tóm tắt nhóm":     g.get("summary", ""),
                                    "Phản hồi nhà trường": g.get("suggested_response", ""),
                                    "Câu":              fb.get("question", ""),
                                    "Ngành":            fb.get("major", ""),
                                    "Nội dung góp ý":   fb.get("content", ""),
                                })
                        if rows_export:
                            dl_df  = pd.DataFrame(rows_export)
                            dl_csv = dl_df.to_csv(index=False, encoding="utf-8-sig")
                            st.download_button(
                                "📥 Tải kết quả gom nhóm (CSV)",
                                dl_csv.encode("utf-8-sig"),
                                "ai_feedback_groups.csv", "text/csv",
                                use_container_width=True,
                            )
