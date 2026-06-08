# ResumeIQ - AI Resume Analyzer

ResumeIQ is an AI-powered resume analysis backend built with Python, FastAPI, NLP, Scikit-learn, and REST APIs. It compares a resume against a job description, calculates an ATS-style match score, extracts important keywords, identifies missing skills, and generates practical improvement recommendations.

## Features

- Upload and analyze resumes through REST APIs
- Supports `.txt`, `.pdf`, and `.docx` resume files
- Cleans and normalizes resume/job-description text
- Extracts important job keywords with TF-IDF
- Calculates resume-job similarity with cosine similarity
- Produces ATS-style match score, matched keywords, missing keywords, and recommendations
- Includes sample data and automated tests

## Project Structure

```text
app/
  main.py                 FastAPI app and API routes
  models.py               Request and response schemas
  services/
    analyzer.py           Resume analysis workflow
    text_processing.py    Text extraction and NLP preprocessing
samples/
  job_description.txt     Example job description
  resume.txt              Example resume
tests/
  test_analyzer.py        Unit tests for analysis logic
  test_api.py             API tests
requirements.txt
```

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Run The API

```powershell
uvicorn app.main:app --reload
```

Open the docs at:

```text
http://127.0.0.1:8000/docs
```

## API Endpoints

### Health Check

```http
GET /health
```

### Analyze Plain Text

```http
POST /analyze
```

Example JSON:

```json
{
  "resume_text": "Python developer with FastAPI, NLP, machine learning, and REST API experience.",
  "job_description": "Looking for a Python backend developer with FastAPI, NLP, Scikit-learn, REST APIs, and cloud experience."
}
```

### Analyze Uploaded Resume

```http
POST /analyze/upload
```

Form fields:

- `resume_file`: `.txt`, `.pdf`, or `.docx`
- `job_description`: job description text

## Try With PowerShell

```powershell
$body = @{
  resume_text = [string]::Join("`n", (Get-Content -Path .\samples\resume.txt))
  job_description = [string]::Join("`n", (Get-Content -Path .\samples\job_description.txt))
} | ConvertTo-Json

Invoke-RestMethod -Uri http://127.0.0.1:8000/analyze -Method Post -Body $body -ContentType "application/json"
```

## Run Tests

```powershell
pytest
```

## How It Works

1. The API receives resume text or an uploaded resume file.
2. The text processor extracts and cleans text by lowercasing, removing noise, and filtering stop words.
3. The analyzer builds TF-IDF vectors for the resume and job description.
4. Cosine similarity compares both vectors and becomes the base matching score.
5. TF-IDF keyword extraction finds important job keywords.
6. The analyzer separates keywords into matched and missing lists.
7. Recommendations are generated from missing keywords and match strength.

This is a practical starter version of an ATS-style analyzer. In production, it can be expanded with named entity recognition, section parsing, skill taxonomies, historical hiring data, and ranking across many candidates.
