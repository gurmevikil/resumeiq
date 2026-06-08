from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str
    service: str


class AnalysisRequest(BaseModel):
    resume_text: str = Field(..., min_length=20)
    job_description: str = Field(..., min_length=20)


class KeywordMatch(BaseModel):
    keyword: str
    present_in_resume: bool


class AnalysisResponse(BaseModel):
    match_score: float
    match_label: str
    similarity_score: float
    matched_keywords: list[str]
    missing_keywords: list[str]
    keyword_matches: list[KeywordMatch]
    recommendations: list[str]
    resume_word_count: int
    job_word_count: int
