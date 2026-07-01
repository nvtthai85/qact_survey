"""
Orchestrator: Điều phối toàn bộ pipeline phân tích
"""
import pandas as pd
from pathlib import Path
from src.pipeline.data_loader import (
    load_survey, get_all_comments, QUESTION_MAP
)
from src.agents.ai_agents import (
    analyze_sentiment_batch,
    extract_insights,
    generate_executive_summary,
    identify_strengths_bottlenecks,
    generate_checklist,
    generate_action_recommendations,
)


def run_full_analysis(filepath: str, progress_callback=None) -> dict:
    """
    Chạy toàn bộ pipeline phân tích.
    Trả về dict kết quả đầy đủ cho dashboard.
    """
    def log(msg, pct=None):
        if progress_callback:
            progress_callback(msg, pct)

    # ── 1. LOAD & PREPROCESS ─────────────────────────────────
    log("📥 Đang tải và chuẩn hoá dữ liệu...", 5)
    df = load_survey(filepath)
    comments_df = get_all_comments(df)

    total_responses = len(df)
    major_dist      = df["Major"].value_counts().to_dict()
    response_dates  = df["ResponseDate"].dropna()

    # Tính avg satisfaction tổng thể
    score_cols = [f"Q{i}_Score" for i in range(1, 9)]
    all_scores = pd.concat([df[c].dropna() for c in score_cols if c in df.columns])
    avg_satisfaction = all_scores.mean() if len(all_scores) > 0 else 0

    stats = {
        "total":            total_responses,
        "majors":           major_dist,
        "avg_satisfaction": avg_satisfaction,
        "date_range": {
            "min": str(response_dates.min().date()) if len(response_dates) > 0 else "",
            "max": str(response_dates.max().date()) if len(response_dates) > 0 else "",
        }
    }

    # ── 2. SENTIMENT ANALYSIS ────────────────────────────────
    log("💬 Đang phân tích cảm xúc với AI...", 20)
    all_comments = comments_df["Comment"].dropna().tolist()

    if all_comments:
        sentiment_results = analyze_sentiment_batch(all_comments)
        # Gán kết quả vào comments_df
        valid_mask = comments_df["Comment"].notna()
        valid_idx  = comments_df[valid_mask].index
        for i, idx in enumerate(valid_idx):
            if i < len(sentiment_results):
                res = sentiment_results[i]
                comments_df.loc[idx, "AI_Sentiment"]   = res.get("sentiment", "neutral")
                comments_df.loc[idx, "AI_Emotion"]     = res.get("emotion", "trung_lập")
                comments_df.loc[idx, "AI_Confidence"]  = res.get("confidence", 0.5)
                comments_df.loc[idx, "AI_Keywords"] = ", ".join(res.get("keywords", []))
    else:
        comments_df["AI_Sentiment"]  = None
        comments_df["AI_Emotion"]    = None
        comments_df["AI_Confidence"] = None
        comments_df["AI_Keywords"]   = None

    # Tổng hợp sentiment theo nguồn (rating)
    sentiment_summary = {}
    for q_key in QUESTION_MAP:
        sent_col = f"{q_key}_Sentiment"
        if sent_col in df.columns:
            vc = df[sent_col].value_counts()
            total = vc.sum()
            sentiment_summary[q_key] = {
                "positive": int(vc.get("positive", 0)),
                "neutral":  int(vc.get("neutral", 0)),
                "negative": int(vc.get("negative", 0)),
                "total":    int(total),
                "pos_pct":  round(vc.get("positive", 0) / total * 100, 1) if total > 0 else 0,
                "neg_pct":  round(vc.get("negative", 0) / total * 100, 1) if total > 0 else 0,
            }

    # ── 3. INSIGHT EXTRACTION ────────────────────────────────
    log("🔍 Đang trích xuất insight theo từng tiêu chí...", 45)
    all_insights = {}
    for q_key, q_label in QUESTION_MAP.items():
        q_comments = comments_df[comments_df["Question"] == q_key]
        all_insights[q_key] = extract_insights(q_comments, q_label)

    # ── 4. EXECUTIVE SUMMARY ────────────────────────────────
    log("📊 Đang tạo tóm tắt điều hành...", 62)
    executive_summary = generate_executive_summary(all_insights, stats)

    # ── 5. STRENGTH & BOTTLENECK ────────────────────────────
    log("💪 Đang nhận diện điểm mạnh & điểm nghẽn...", 72)
    sb_result = identify_strengths_bottlenecks(df)

    # ── 6. CHECKLIST & ALERT ────────────────────────────────
    log("✅ Đang tạo checklist & cảnh báo...", 85)
    checklist = generate_checklist(df)

    # ── 7. ACTION RECOMMENDATIONS ───────────────────────────
    log("💡 Đang tạo đề xuất hành động...", 92)
    actions = generate_action_recommendations(
        sb_result["bottlenecks"], checklist, all_insights
    )

    log("✅ Phân tích hoàn tất!", 100)

    return {
        "stats":             stats,
        "df":                df,
        "comments_df":       comments_df,
        "sentiment_summary": sentiment_summary,
        "all_insights":      all_insights,
        "executive_summary": executive_summary,
        "strengths":         sb_result["strengths"],
        "bottlenecks":       sb_result["bottlenecks"],
        "watch_list":        sb_result["watch_list"],
        "question_stats":    sb_result["stats"],
        "checklist":         checklist,
        "actions":           actions,
    }
