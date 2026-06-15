"""
AI Service Mock – FIT4110 Lab 05

Cung cấp các endpoint:
  GET  /health   – kiểm tra trạng thái service
  POST /predict  – phân tích dữ liệu cảm biến, trả kết quả mock AI

Nhóm có thể thay thế logic trong predict() bằng mô hình thực tế
(YOLOv8, MediaPipe, scikit-learn, …).
"""

import os
from datetime import datetime, timezone
from typing import Dict, List, Optional

from fastapi import FastAPI
from pydantic import BaseModel

# Đọc biến môi trường
AI_SERVICE_NAME = os.getenv("AI_SERVICE_NAME", "ai-service")
AI_SERVICE_VERSION = os.getenv("AI_SERVICE_VERSION", "0.1.0")

app = FastAPI(
    title="FIT4110 Lab 05 – AI Service",
    version=AI_SERVICE_VERSION,
    description=(
        "Mock AI service chạy trong Docker Compose stack. "
        "Nhận dữ liệu cảm biến và trả kết quả phân tích AI mô phỏng."
    ),
)


# ─────────────────────────────────────────
# Schema
# ─────────────────────────────────────────

class HealthResponse(BaseModel):
    status: str
    service: str
    version: str


class PredictRequest(BaseModel):
    device_id: Optional[str] = None
    metric: Optional[str] = None
    value: Optional[float] = None


class PredictionResult(BaseModel):
    device_id: Optional[str]
    metric: Optional[str]
    labels: List[str]
    confidence: List[float]
    anomaly_detected: bool
    anomaly_score: float
    recommendation: str
    analyzed_at: str


# ─────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def mock_analyze(metric: Optional[str], value: Optional[float]) -> Dict:
    """
    Giả lập kết quả phân tích AI dựa trên metric và value.
    Thay thế hàm này bằng model thực tế nếu cần.
    """
    if metric == "temperature":
        if value is not None and value >= 60:
            return {
                "labels": ["high_temperature", "fire_risk"],
                "confidence": [0.97, 0.82],
                "anomaly_detected": True,
                "anomaly_score": 0.91,
                "recommendation": "Kiểm tra ngay khu vực cảm biến – nhiệt độ nguy hiểm!",
            }
        elif value is not None and value >= 40:
            return {
                "labels": ["elevated_temperature"],
                "confidence": [0.85],
                "anomaly_detected": True,
                "anomaly_score": 0.55,
                "recommendation": "Theo dõi xu hướng nhiệt độ trong 15 phút tiếp theo.",
            }
        else:
            return {
                "labels": ["normal_temperature"],
                "confidence": [0.99],
                "anomaly_detected": False,
                "anomaly_score": 0.05,
                "recommendation": "Nhiệt độ bình thường. Không cần hành động.",
            }
    elif metric == "smoke":
        if value is not None and value >= 300:
            return {
                "labels": ["smoke_detected", "evacuation_required"],
                "confidence": [0.99, 0.95],
                "anomaly_detected": True,
                "anomaly_score": 0.98,
                "recommendation": "CẢNH BÁO: Phát hiện khói! Kích hoạt báo động và sơ tán.",
            }
        else:
            return {
                "labels": ["normal_air_quality"],
                "confidence": [0.96],
                "anomaly_detected": False,
                "anomaly_score": 0.03,
                "recommendation": "Chất lượng không khí bình thường.",
            }
    elif metric == "motion":
        return {
            "labels": ["motion_detected" if value else "no_motion"],
            "confidence": [0.93],
            "anomaly_detected": False,
            "anomaly_score": 0.10,
            "recommendation": "Chuyển động ghi nhận, không có bất thường.",
        }
    else:
        return {
            "labels": ["unknown_metric"],
            "confidence": [0.70],
            "anomaly_detected": False,
            "anomaly_score": 0.20,
            "recommendation": "Metric chưa được nhận diện, cần thêm dữ liệu huấn luyện.",
        }


# ─────────────────────────────────────────
# Endpoints
# ─────────────────────────────────────────

@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    """Kiểm tra trạng thái AI service."""
    return HealthResponse(
        status="ok",
        service=AI_SERVICE_NAME,
        version=AI_SERVICE_VERSION,
    )


@app.post("/predict", response_model=PredictionResult)
def predict(payload: PredictRequest = PredictRequest()) -> PredictionResult:
    """
    Phân tích dữ liệu cảm biến và trả kết quả AI.

    Nhận: device_id, metric, value (tuỳ chọn)
    Trả:  labels, confidence, anomaly_detected, anomaly_score, recommendation
    """
    analysis = mock_analyze(payload.metric, payload.value)

    return PredictionResult(
        device_id=payload.device_id,
        metric=payload.metric,
        labels=analysis["labels"],
        confidence=analysis["confidence"],
        anomaly_detected=analysis["anomaly_detected"],
        anomaly_score=analysis["anomaly_score"],
        recommendation=analysis["recommendation"],
        analyzed_at=now_iso(),
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9000)