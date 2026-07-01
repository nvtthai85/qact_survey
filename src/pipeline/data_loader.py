"""
Data Loader & Preprocessor
Đọc file Excel khảo sát, chuẩn hoá dữ liệu, phân loại câu trả lời
"""
import pandas as pd
import re
from pathlib import Path

# ── Mapping câu hỏi ──────────────────────────────────────────────────────────
QUESTION_MAP = {
    "Q1": "Chương trình đào tạo",
    "Q2": "Tổ chức đào tạo",
    "Q3": "Tài nguyên học tập & CSVC",
    "Q4": "Giảng dạy & Đội ngũ GV",
    "Q5": "Tinh thần phục vụ",
    "Q6": "Hỗ trợ sinh viên",
    "Q7": "Hoạt động truyền thống",
    "Q8": "Tổng thể trải nghiệm",
}

# ── Mapping rating → điểm số ─────────────────────────────────────────────────
RATING_SCORE = {
    "Rất hài lòng/ Very satisfied":       5,
    "Rất hài lòng":                        5,
    "Very satisfied":                       5,
    "Hài lòng/ Satisfied":                 4,
    "Hài lòng":                             4,
    "Satisfied":                            4,
    "Bình thường/ Normal":                 3,
    "Phân vân/ Neutral":                   3,
    "Bình thường":                          3,
    "Normal":                               3,
    "Không hài lòng/ Dissatisfied":        2,
    "Không hài lòng":                      2,
    "Dissatisfied":                         2,
    "Rất không hài lòng/ Very dissatisfied": 1,
    "Rất không hài lòng":                  1,
    "Very dissatisfied":                    1,
}

RATING_SENTIMENT = {
    5: "positive",
    4: "positive",
    3: "neutral",
    2: "negative",
    1: "negative",
}

MAJOR_MAP = {
    "Quản trị kinh doanh": "Quản trị kinh doanh",
    "Công nghệ thông tin":  "Công nghệ thông tin",
    "Ngôn ngữ":             "Ngôn ngữ",
}


def load_survey(filepath: str) -> pd.DataFrame:
    """Đọc file Excel và trả về DataFrame đã chuẩn hoá."""
    df = pd.read_excel(filepath, sheet_name="Answer")

    # Đổi tên cột ngắn gọn
    col_mapping = {
        df.columns[0]:  "Email",
        df.columns[1]:  "Name",
        df.columns[2]:  "Code",
        df.columns[3]:  "ResponseDate",
        df.columns[4]:  "Major",
        df.columns[5]:  "Q1_Rating",
        df.columns[6]:  "Q1_Comment",
        df.columns[7]:  "Q2_Rating",
        df.columns[8]:  "Q2_Comment",
        df.columns[9]:  "Q3_Rating",
        df.columns[10]: "Q3_Comment",
        df.columns[11]: "Q4_Rating",
        df.columns[12]: "Q4_Comment",
        df.columns[13]: "Q5_Rating",
        df.columns[14]: "Q5_Comment",
        df.columns[15]: "Q6_Rating",
        df.columns[16]: "Q6_Comment",
        df.columns[17]: "Q7_Rating",
        df.columns[18]: "Q7_Comment",
        df.columns[19]: "Q8_Rating",
        df.columns[20]: "Q8_Comment",
    }
    df = df.rename(columns=col_mapping)

    # Chuẩn hoá Major
    df["Major"] = df["Major"].apply(_normalize_major)

    # Chuyển rating → điểm số & sentiment
    for q in ["Q1","Q2","Q3","Q4","Q5","Q6","Q7","Q8"]:
        df[f"{q}_Score"]     = df[f"{q}_Rating"].map(RATING_SCORE)
        df[f"{q}_Sentiment"] = df[f"{q}_Score"].map(RATING_SENTIMENT)

    # Lọc bỏ comment rác ("Ko có", "không", blank...)
    for q in ["Q1","Q2","Q3","Q4","Q5","Q6","Q7","Q8"]:
        df[f"{q}_Comment"] = df[f"{q}_Comment"].apply(_clean_comment)

    # ResponseDate
    df["ResponseDate"] = pd.to_datetime(df["ResponseDate"], errors="coerce")

    return df


def _normalize_major(raw: str) -> str:
    if not isinstance(raw, str):
        return "Khác"
    raw_lower = raw.lower()
    if "quản trị" in raw_lower or "business" in raw_lower:
        return "Quản trị kinh doanh"
    if "công nghệ" in raw_lower or "it" in raw_lower or "information" in raw_lower:
        return "Công nghệ thông tin"
    if "ngôn ngữ" in raw_lower or "language" in raw_lower:
        return "Ngôn ngữ"
    return "Khác"


def _clean_comment(text) -> str:
    """Trả về None nếu comment rác, ngược lại trả về text sạch."""
    if not isinstance(text, str):
        return None
    text = text.strip()
    # Loại bỏ các câu rỗng ý nghĩa
    noise_patterns = [
        r"^(ko|không|none|chưa|chua|ổn|ok|oke|binh thuong|bình thường|n/a|na)\s*$",
        r"^(hi vọng|.{0,3})$",  # quá ngắn
    ]
    for pat in noise_patterns:
        if re.match(pat, text, re.IGNORECASE):
            return None
    if len(text) < 8:
        return None
    return text


def get_all_comments(df: pd.DataFrame) -> pd.DataFrame:
    """Gộp tất cả comment thành bảng dài (long format)."""
    records = []
    for q_key, q_label in QUESTION_MAP.items():
        col = f"{q_key}_Comment"
        score_col = f"{q_key}_Score"
        sent_col  = f"{q_key}_Sentiment"
        for _, row in df.iterrows():
            if row.get(col):
                records.append({
                    "Question":  q_key,
                    "QLabel":    q_label,
                    "Comment":   row[col],
                    "Score":     row.get(score_col),
                    "Sentiment": row.get(sent_col),
                    "Major":     row.get("Major"),
                    "Name":      row.get("Name"),
                })
    return pd.DataFrame(records)
