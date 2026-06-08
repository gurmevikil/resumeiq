from app.services.analyzer import ResumeAnalyzer


def test_analyzer_returns_match_score_and_keywords() -> None:
    analyzer = ResumeAnalyzer(max_keywords=10)

    result = analyzer.analyze(
        resume_text=(
            "Python FastAPI developer with NLP, Scikit-learn, TF-IDF, "
            "cosine similarity, REST APIs, and backend optimization experience."
        ),
        job_description=(
            "Need Python developer with FastAPI, NLP, Scikit-learn, REST APIs, "
            "resume parsing, keyword extraction, and cosine similarity."
        ),
    )

    assert result.match_score > 50
    assert "python" in result.matched_keywords
    assert result.resume_word_count > 0
    assert result.job_word_count > 0


def test_analyzer_rejects_empty_content() -> None:
    analyzer = ResumeAnalyzer()

    try:
        analyzer.analyze("!!!", "Python FastAPI NLP developer role")
    except ValueError as exc:
        assert "Resume text" in str(exc)
    else:
        raise AssertionError("Expected ValueError")
