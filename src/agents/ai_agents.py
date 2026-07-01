"""
AI Agents: Sentiment, Insight, Bottleneck, Checklist/Alert
Dùng OpenAI GPT để phân tích dữ liệu khảo sát
"""
import os
import json
import time
from typing import Optional
import pandas as pd
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

_client = None
_last_api_key = None

def _get_client() -> OpenAI:
    global _client, _last_api_key
    current_key = os.getenv("OPENAI_API_KEY")
    if _client is None or current_key != _last_api_key:
        _client = OpenAI(api_key=current_key)
        _last_api_key = current_key
    return _client

MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")


# ═══════════════════════════════════════════════════════════════
# HELPER
# ═══════════════════════════════════════════════════════════════
def _chat(system: str, user: str, max_tokens: int = 1500) -> str:
    """Gọi OpenAI ChatCompletion với retry đơn giản."""
    current_model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    for attempt in range(3):
        try:
            resp = _get_client().chat.completions.create(
                model=current_model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user",   "content": user},
                ],
                max_tokens=max_tokens,
                temperature=0.3,
                response_format={"type": "json_object"},
            )
            return resp.choices[0].message.content
        except Exception as e:
            if attempt == 2:
                raise
            time.sleep(2 ** attempt)


# ═══════════════════════════════════════════════════════════════
# AGENT 1: SENTIMENT ANALYSIS
# ═══════════════════════════════════════════════════════════════
def analyze_sentiment_batch(comments: list[str]) -> list[dict]:
    """
    Phân tích cảm xúc cho danh sách comment.
    Trả về list dict: {sentiment, emotion, confidence, keywords}
    """
    if not comments:
        return []

    # Batch tối đa 20 comments mỗi lần gọi API
    results = []
    batch_size = 20
    for i in range(0, len(comments), batch_size):
        batch = comments[i:i+batch_size]
        numbered = "\n".join([f"{j+1}. {c}" for j, c in enumerate(batch)])

        system = """Bạn là chuyên gia phân tích cảm xúc khảo sát giáo dục tiếng Việt.
Phân tích từng câu phản hồi và trả về JSON theo format:
{
  "results": [
    {
      "sentiment": "positive|negative|neutral",
      "emotion": "hài_lòng|thất_vọng|lo_ngại|tích_cực|trung_lập|đề_xuất",
      "confidence": 0.0-1.0,
      "keywords": ["từ_khoá_1", "từ_khoá_2"]
    }
  ]
}
Số phần tử trong results phải bằng số câu đầu vào."""

        user = f"Phân tích {len(batch)} câu phản hồi sau:\n{numbered}"

        try:
            raw = _chat(system, user, max_tokens=2000)
            data = json.loads(raw)
            results.extend(data.get("results", [{}] * len(batch)))
        except Exception:
            results.extend([{"sentiment": "neutral", "emotion": "trung_lập",
                             "confidence": 0.5, "keywords": []}] * len(batch))

    return results


# ═══════════════════════════════════════════════════════════════
# AGENT 2: INSIGHT ANALYSIS
# ═══════════════════════════════════════════════════════════════
def extract_insights(comments_df: pd.DataFrame, question_label: str) -> dict:
    """
    Phân tích insight cho một nhóm câu hỏi.
    Input: DataFrame với cột [Comment, Sentiment, Major]
    Output: dict với topics, keywords, trends, summary
    """
    valid_comments = comments_df["Comment"].dropna().tolist()
    if len(valid_comments) < 2:
        return {
            "topics": [],
            "keywords": [],
            "summary": "Không đủ dữ liệu để phân tích.",
            "positive_themes": [],
            "negative_themes": [],
        }

    sample = valid_comments[:50]  # Giới hạn token
    comments_text = "\n".join([f"- {c}" for c in sample])

    system = """Bạn là chuyên gia phân tích khảo sát giáo dục đại học tại Việt Nam.
Phân tích các phản hồi và trả về JSON:
{
  "summary": "Tóm tắt ngắn gọn 2-3 câu về nhóm phản hồi này",
  "topics": [
    {"topic": "tên chủ đề", "count": số_lần_đề_cập, "sentiment": "positive|negative|neutral"}
  ],
  "keywords": ["từ khoá nổi bật 1", "từ khoá 2", "..."],
  "positive_themes": ["điểm được đánh giá tốt 1", "điểm 2"],
  "negative_themes": ["vấn đề được phản ánh 1", "vấn đề 2"],
  "recommendations": ["đề xuất cải thiện 1", "đề xuất 2"]
}"""

    user = f"""Câu hỏi: "{question_label}"
Tổng {len(valid_comments)} phản hồi, đây là mẫu {len(sample)} phản hồi:
{comments_text}"""

    try:
        raw = _chat(system, user, max_tokens=1500)
        return json.loads(raw)
    except Exception as e:
        return {
            "summary": f"Lỗi phân tích: {e}",
            "topics": [], "keywords": [],
            "positive_themes": [], "negative_themes": [],
            "recommendations": [],
        }


def generate_executive_summary(all_insights: dict, stats: dict) -> dict:
    """Tạo Executive Summary tổng thể từ tất cả kết quả."""
    summaries_text = "\n".join([
        f"- {q}: {data.get('summary', '')}"
        for q, data in all_insights.items()
    ])

    system = """Bạn là chuyên gia tư vấn giáo dục đại học.
Tổng hợp kết quả khảo sát sinh viên và trả về JSON:
{
  "headline": "Tiêu đề chính của báo cáo (1 câu ấn tượng)",
  "overview": "Tổng quan 3-4 câu về kết quả khảo sát",
  "top_insights": [
    {"rank": 1, "insight": "insight quan trọng nhất", "impact": "high|medium|low"},
    {"rank": 2, "insight": "...", "impact": "..."},
    {"rank": 3, "insight": "...", "impact": "..."}
  ],
  "overall_sentiment": "Đánh giá chung về cảm xúc tổng thể",
  "key_action": "Hành động ưu tiên cao nhất cần thực hiện ngay"
}"""

    user = f"""Kết quả khảo sát: {stats.get('total', 0)} sinh viên, {stats.get('majors', {})}
Tỷ lệ hài lòng trung bình: {stats.get('avg_satisfaction', 0):.1f}/5
Tổng hợp từng câu hỏi:
{summaries_text}"""

    try:
        raw = _chat(system, user, max_tokens=1000)
        return json.loads(raw)
    except Exception:
        return {
            "headline": "Kết quả Khảo Sát Sinh Viên",
            "overview": "Đang xử lý dữ liệu...",
            "top_insights": [],
            "overall_sentiment": "Đang phân tích",
            "key_action": "",
        }


# ═══════════════════════════════════════════════════════════════
# AGENT 3: STRENGTH & BOTTLENECK
# ═══════════════════════════════════════════════════════════════
def identify_strengths_bottlenecks(df: pd.DataFrame) -> dict:
    """
    Nhận diện điểm mạnh và điểm nghẽn dựa trên rating + comment.
    Trả về: {strengths: [...], bottlenecks: [...], watch_list: [...]}
    """
    from src.pipeline.data_loader import QUESTION_MAP

    question_stats = {}
    for q_key, q_label in QUESTION_MAP.items():
        score_col = f"{q_key}_Score"
        sent_col  = f"{q_key}_Sentiment"
        if score_col not in df.columns:
            continue
        scores = df[score_col].dropna()
        sentiments = df[sent_col].dropna()

        pos_rate = (sentiments == "positive").mean() if len(sentiments) > 0 else 0
        neg_rate = (sentiments == "negative").mean() if len(sentiments) > 0 else 0
        avg      = scores.mean() if len(scores) > 0 else 0

        question_stats[q_key] = {
            "label":    q_label,
            "avg":      round(avg, 2),
            "pos_rate": round(pos_rate * 100, 1),
            "neg_rate": round(neg_rate * 100, 1),
            "total":    len(scores),
        }

    # Phân loại dựa trên ngưỡng
    strengths   = []
    bottlenecks = []
    watch_list  = []

    for q_key, stat in question_stats.items():
        entry = {
            "question": q_key,
            "label":    stat["label"],
            "avg":      stat["avg"],
            "pos_rate": stat["pos_rate"],
            "neg_rate": stat["neg_rate"],
        }
        if stat["avg"] >= 4.2 and stat["pos_rate"] >= 70:
            strengths.append(entry)
        elif stat["avg"] < 3.5 or stat["neg_rate"] >= 20:
            bottlenecks.append(entry)
        else:
            watch_list.append(entry)

    # Sắp xếp
    strengths.sort(key=lambda x: -x["avg"])
    bottlenecks.sort(key=lambda x: x["avg"])

    return {
        "strengths":   strengths,
        "bottlenecks": bottlenecks,
        "watch_list":  watch_list,
        "stats":       question_stats,
    }


# ═══════════════════════════════════════════════════════════════
# AGENT 4: CHECKLIST & ALERT
# ═══════════════════════════════════════════════════════════════
CHECKLIST_CONFIG = {
    "Chất lượng giảng dạy": {
        "questions":    ["Q1", "Q2", "Q4"],
        "kpi_name":     "Điểm hài lòng trung bình",
        "warn_below":   3.8,
        "critical_below": 3.5,
        "unit":         "/5",
        "icon":         "📚",
    },
    "Cơ sở vật chất & Tài nguyên": {
        "questions":    ["Q3"],
        "kpi_name":     "Tỷ lệ phản hồi tiêu cực",
        "warn_above":   15.0,
        "critical_above": 25.0,
        "unit":         "%",
        "icon":         "🏫",
    },
    "Hỗ trợ & Dịch vụ sinh viên": {
        "questions":    ["Q5", "Q6", "Q7"],
        "kpi_name":     "Điểm hài lòng trung bình",
        "warn_below":   3.8,
        "critical_below": 3.5,
        "unit":         "/5",
        "icon":         "🎓",
    },
}


def generate_checklist(df: pd.DataFrame) -> list[dict]:
    """
    Tạo checklist KPI với trạng thái cảnh báo.
    Trả về list các mục checklist.
    """
    items = []

    for group_name, config in CHECKLIST_CONFIG.items():
        q_keys  = config["questions"]
        icon    = config["icon"]
        unit    = config["unit"]
        kpi_name = config["kpi_name"]

        # Tính KPI
        if unit == "/5":
            scores = []
            for q in q_keys:
                col = f"{q}_Score"
                if col in df.columns:
                    scores.extend(df[col].dropna().tolist())
            kpi_value = round(sum(scores) / len(scores), 2) if scores else 0.0

            warn_thr     = config.get("warn_below", 3.8)
            critical_thr = config.get("critical_below", 3.5)

            if kpi_value < critical_thr:
                status = "critical"; status_icon = "🔴"
                alert = f"Điểm trung bình {kpi_value}/5 — DƯỚI ngưỡng nguy hiểm!"
            elif kpi_value < warn_thr:
                status = "warning"; status_icon = "⚠️"
                alert = f"Điểm trung bình {kpi_value}/5 — Cần chú ý cải thiện."
            else:
                status = "ok"; status_icon = "✅"
                alert = f"Đạt yêu cầu ({kpi_value}/5)"

        else:  # unit == "%"
            neg_rates = []
            for q in q_keys:
                sent_col = f"{q}_Sentiment"
                if sent_col in df.columns:
                    sentiments = df[sent_col].dropna()
                    if len(sentiments) > 0:
                        neg_rate = (sentiments == "negative").mean() * 100
                        neg_rates.append(neg_rate)
            kpi_value = round(sum(neg_rates) / len(neg_rates), 1) if neg_rates else 0.0

            warn_thr     = config.get("warn_above", 15.0)
            critical_thr = config.get("critical_above", 25.0)

            if kpi_value > critical_thr:
                status = "critical"; status_icon = "🔴"
                alert = f"{kpi_value}% phản hồi tiêu cực — Vượt ngưỡng nguy hiểm!"
            elif kpi_value > warn_thr:
                status = "warning"; status_icon = "⚠️"
                alert = f"{kpi_value}% phản hồi tiêu cực — Cần theo dõi."
            else:
                status = "ok"; status_icon = "✅"
                alert = f"Bình thường ({kpi_value}%)"

        items.append({
            "group":       group_name,
            "icon":        icon,
            "kpi_name":    kpi_name,
            "kpi_value":   kpi_value,
            "unit":        unit,
            "status":      status,
            "status_icon": status_icon,
            "alert":       alert,
            "questions":   q_keys,
        })

    return items


def generate_action_recommendations(
    bottlenecks: list[dict],
    checklist:   list[dict],
    all_insights: dict,
) -> list[dict]:
    """Dùng AI tạo đề xuất hành động ưu tiên."""
    bottleneck_text = "\n".join([
        f"- {b['label']}: điểm {b['avg']}/5, tiêu cực {b['neg_rate']}%"
        for b in bottlenecks
    ]) or "Không có điểm nghẽn đáng kể"

    alert_text = "\n".join([
        f"- {c['group']}: {c['alert']}"
        for c in checklist if c["status"] in ("warning", "critical")
    ]) or "Không có cảnh báo"

    system = """Bạn là chuyên gia tư vấn cải tiến chất lượng giáo dục đại học Việt Nam.
Đưa ra các đề xuất hành động cụ thể, khả thi. Trả về JSON:
{
  "actions": [
    {
      "priority": "high|medium|low",
      "category": "Chất lượng giảng dạy|Cơ sở vật chất|Hỗ trợ sinh viên|Chương trình",
      "action": "Mô tả hành động cụ thể",
      "timeline": "Ngay lập tức|1 tháng|1 học kỳ|Dài hạn",
      "expected_impact": "Tác động kỳ vọng"
    }
  ]
}
Đề xuất 5-7 hành động, sắp xếp theo ưu tiên."""

    user = f"""Điểm nghẽn phát hiện:
{bottleneck_text}

Cảnh báo checklist:
{alert_text}"""

    try:
        raw = _chat(system, user, max_tokens=1500)
        data = json.loads(raw)
        return data.get("actions", [])
    except Exception:
        return []


# ═══════════════════════════════════════════════════════════════
# AGENT 5: FEEDBACK GROUPING (dùng đúng prompt từ KS_Survey.html)
# ═══════════════════════════════════════════════════════════════
def group_feedbacks(feedbacks: list[dict], progress_callback=None) -> dict:
    """
    Gom nhóm ý kiến đóng góp bằng AI.
    Input : list[{stt, question, content, major}]
    Output: {groups, total_feedbacks, total_groups, model_used}
    Dùng đúng prompt chuẩn từ KS_Survey.html v2.2
    """
    if not feedbacks:
        return {"groups": [], "total_feedbacks": 0, "total_groups": 0}

    def log(msg):
        if progress_callback:
            progress_callback(msg)

    # Nhóm theo câu hỏi (giống HTML)
    fb_by_q: dict[str, list] = {}
    for fb in feedbacks:
        q = fb.get("question", "Câu ?")
        fb_by_q.setdefault(q, []).append(fb)

    fb_text = ""
    for q, items in fb_by_q.items():
        fb_text += f"\n=== {q} ===\n"
        for it in items:
            fb_text += f"[#{it['stt']} | {it['major']}] {it['content']}\n"

    system = """Bạn là chuyên gia phân tích khảo sát giáo dục đại học tại FPT Education.
Nhiệm vụ: Phân tích, gom nhóm các ý kiến đóng góp của sinh viên, VÀ đề xuất phản hồi chính thức cho từng nhóm.

QUY TẮC BẮT BUỘC:
1. Đọc TẤT CẢ ý kiến, tìm các ý kiến có hàm ý/nội dung giống hoặc tương tự nhau → gom thành 1 nhóm
2. Mỗi nhóm: tên nhóm ngắn gọn, tóm tắt chuyên gia súc tích, danh sách ID ý kiến thuộc nhóm
3. Phân loại sentiment: positive (tích cực), negative (tiêu cực), neutral (trung lập), suggestion (đề xuất)
4. GỢI Ý PHẢN HỒI từ nhà trường: Ghi nhận ý kiến, với tiêu cực/đề xuất nêu hướng cải thiện cụ thể. Ngắn gọn 2-4 câu, chuyên nghiệp, ấm áp.

TRẢ VỀ JSON:
{
  "groups": [
    {
      "name": "Tên nhóm",
      "question_scope": "Câu 1 hoặc Nhiều câu",
      "sentiment": "positive|negative|neutral|suggestion",
      "summary": "Tóm tắt chuyên gia",
      "suggested_response": "Gợi ý phản hồi chính thức từ nhà trường",
      "feedback_ids": [1, 5, 12],
      "count": 3
    }
  ],
  "total_feedbacks": 50,
  "total_groups": 8
}"""

    user = f"Phân tích và gom nhóm {len(feedbacks)} ý kiến dưới đây. Trả về JSON đúng format.\n\n{fb_text}"

    log(f"Đang gom nhóm {len(feedbacks)} ý kiến với AI...")

    current_model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    seen: set = set()
    models_to_try = [m for m in [current_model, "gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"]
                     if not (m in seen or seen.add(m))]

    last_error = None
    for model in models_to_try:
        for attempt in range(2):
            try:
                log(f"Gọi {model} (lần {attempt + 1})...")
                resp = _get_client().chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": system},
                        {"role": "user",   "content": user},
                    ],
                    max_tokens=8000,
                    temperature=0.3,
                    response_format={"type": "json_object"},
                )
                data = json.loads(resp.choices[0].message.content)
                groups = data.get("groups", [])
                fb_map = {fb["stt"]: fb for fb in feedbacks}
                for g in groups:
                    g["count"]     = len(g.get("feedback_ids", []))
                    g["originals"] = [fb_map[fid] for fid in g.get("feedback_ids", [])
                                      if fid in fb_map]
                log(f"Hoàn tất: {len(groups)} nhóm ý kiến")
                return {
                    "groups":          groups,
                    "total_feedbacks": data.get("total_feedbacks", len(feedbacks)),
                    "total_groups":    data.get("total_groups", len(groups)),
                    "model_used":      model,
                }
            except Exception as e:
                last_error = e
                time.sleep(2 ** attempt)
        log(f"{model} thất bại, thử model tiếp theo...")

    raise RuntimeError(f"Tất cả model thất bại. Lỗi cuối: {repr(last_error)}")
