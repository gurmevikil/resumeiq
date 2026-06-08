from fastapi import FastAPI, File, Form, HTTPException, UploadFile

from app.models import AnalysisRequest, AnalysisResponse, HealthResponse
from app.services.analyzer import ResumeAnalyzer
from app.services.text_processing import extract_text_from_upload

app = FastAPI(
    title="ResumeIQ - AI Resume Analyzer",
    description="AI-powered ATS resume matching and recommendation API.",
    version="1.0.0",
)

analyzer = ResumeAnalyzer()


@app.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    return HealthResponse(status="ok", service="ResumeIQ")


@app.post("/analyze", response_model=AnalysisResponse)
def analyze_resume(payload: AnalysisRequest) -> AnalysisResponse:
    try:
        return analyzer.analyze(payload.resume_text, payload.job_description)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/analyze/upload", response_model=AnalysisResponse)
async def analyze_uploaded_resume(
    resume_file: UploadFile = File(...),
    job_description: str = Form(...),
) -> AnalysisResponse:
    try:
        resume_text = await extract_text_from_upload(resume_file)
        return analyzer.analyze(resume_text, job_description)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
