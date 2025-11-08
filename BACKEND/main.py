from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import torch
import uvicorn
from typing import Optional
import time

# Initialize FastAPI
app = FastAPI(title="TrustNet AI", version="1.0")

# Update CORS settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5500", "http://127.0.0.1:5500", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# AI Models
class TextDetector:
    def __init__(self):
        self.device = 0 if torch.cuda.is_available() else -1
        try:
            self.detector = pipeline(
                "text-classification",
                model="microsoft/DialoGPT-medium",
                device=self.device
            )
        except:
            self.detector = None
    
    def analyze(self, text: str) -> dict:
        if not self.detector:
            return self.fallback_analysis(text)
        
        try:
            result = self.detector(text[:512])[0]
            ai_score = result['score'] if result['label'] == 'AI' else 1 - result['score']
            
            return {
                "ai_score": round(ai_score * 100, 1),
                "confidence": round(result['score'] * 100, 1),
                "detected_model": self.detect_model_pattern(text, ai_score),
                "reasoning": self.generate_reasoning(ai_score, text),
                "risk_level": self.get_risk_level(ai_score)
            }
        except:
            return self.fallback_analysis(text)
    
    def fallback_analysis(self, text: str) -> dict:
        # Pattern-based fallback
        ai_patterns = ['delve', 'leverage', 'comprehensive', 'robust', 'paradigm']
        text_lower = text.lower()
        matches = sum(1 for pattern in ai_patterns if pattern in text_lower)
        
        ai_score = min(95, matches * 20 + 10)  # Base score
        confidence = max(70, 100 - abs(ai_score - 50))
        
        return {
            "ai_score": ai_score,
            "confidence": confidence,
            "detected_model": "GPT-like" if ai_score > 60 else "Human",
            "reasoning": f"Found {matches} AI language patterns",
            "risk_level": self.get_risk_level(ai_score)
        }
    
    def detect_model_pattern(self, text: str, score: float) -> str:
        if score < 40:
            return "Likely Human"
        text_lower = text.lower()
        if any(word in text_lower for word in ['delve', 'leverage']):
            return "GPT-4"
        elif any(word in text_lower for word in ['comprehensive', 'robust']):
            return "GPT-3.5/Claude"
        else:
            return "Generic AI"
    
    def generate_reasoning(self, score: float, text: str) -> str:
        if score > 80:
            return "High confidence AI-generated content detected"
        elif score > 60:
            return "Likely AI-generated with some human elements"
        elif score > 40:
            return "Mixed signals - could be AI-assisted"
        else:
            return "Appears human-written"
    
    def get_risk_level(self, score: float) -> str:
        if score > 80: return "HIGH"
        elif score > 60: return "MEDIUM"
        elif score > 40: return "LOW"
        else: return "VERY LOW"

# Initialize detector
detector = TextDetector()

# Request models
class AnalysisRequest(BaseModel):
    text: str
    model: Optional[str] = "auto"

# API Routes
@app.get("/")
async def root():
    return {
        "service": "TrustNet AI",
        "status": "active",
        "version": "1.0.0"
    }

@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": time.time()}

@app.post("/analyze")
async def analyze_text(request: AnalysisRequest):
    if len(request.text.strip()) < 10:
        raise HTTPException(400, "Text too short")
    
    result = detector.analyze(request.text)
    
    return {
        "success": True,
        "analysis": result,
        "timestamp": time.time()
    }

if __name__ == "__main__":
    print("🚀 TrustNet AI Backend Starting...")
    print("📍 http://localhost:8000")
    print("📚 Docs: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)