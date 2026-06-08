from collections import Counter

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.models import AnalysisResponse, KeywordMatch
from app.services.text_processing import normalized_text, tokenize, word_count

TECH_KEYWORD_PRIORITY = {
    "python",
    "fastapi",
    "nlp",
    "scikit",
    "learn",
    "api",
    "apis",
    "rest",
    "tf",
    "idf",
    "cosine",
    "similarity",
    "machine",
    "learning",
}


class ResumeAnalyzer:
    def __init__(self, max_keywords: int = 18) -> None:
        self.max_keywords = max_keywords

    def analyze(self, resume_text: str, job_description: str) -> AnalysisResponse:
        resume_normalized = normalized_text(resume_text)
        job_normalized = normalized_text(job_description)

        if not resume_normalized:
            raise ValueError("Resume text does not contain enough readable content.")
        if not job_normalized:
            raise ValueError("Job description does not contain enough readable content.")

        similarity = self._similarity_score(resume_normalized, job_normalized)
        token_overlap = self._token_overlap_score(resume_normalized, job_normalized)
        job_keywords = self._extract_keywords(job_normalized)
        resume_tokens = set(tokenize(resume_text))

        keyword_matches = [
            KeywordMatch(keyword=keyword, present_in_resume=keyword in resume_tokens)
            for keyword in job_keywords
        ]
        matched = [item.keyword for item in keyword_matches if item.present_in_resume]
        missing = [item.keyword for item in keyword_matches if not item.present_in_resume]

        keyword_coverage = len(matched) / len(job_keywords) if job_keywords else 0
        match_score = round(
            ((similarity * 0.25) + (keyword_coverage * 0.45) + (token_overlap * 0.3))
            * 100,
            2,
        )

        return AnalysisResponse(
            match_score=match_score,
            match_label=self._match_label(match_score),
            similarity_score=round(similarity, 4),
            matched_keywords=matched,
            missing_keywords=missing,
            keyword_matches=keyword_matches,
            recommendations=self._recommendations(match_score, missing),
            resume_word_count=word_count(resume_text),
            job_word_count=word_count(job_description),
        )

    def _similarity_score(self, resume_text: str, job_description: str) -> float:
        vectorizer = TfidfVectorizer(ngram_range=(1, 2), min_df=1)
        matrix = vectorizer.fit_transform([resume_text, job_description])
        return float(cosine_similarity(matrix[0:1], matrix[1:2])[0][0])

    def _token_overlap_score(self, resume_text: str, job_description: str) -> float:
        resume_tokens = set(tokenize(resume_text))
        job_tokens = set(tokenize(job_description))
        if not job_tokens:
            return 0.0
        return len(resume_tokens & job_tokens) / len(job_tokens)

    def _extract_keywords(self, job_text: str) -> list[str]:
        vectorizer = TfidfVectorizer(ngram_range=(1, 1), min_df=1)
        matrix = vectorizer.fit_transform([job_text])
        scores = matrix.toarray()[0]
        terms = vectorizer.get_feature_names_out()

        frequency = Counter(tokenize(job_text))
        scored_terms = sorted(
            zip(terms, scores, strict=True),
            key=lambda item: (
                -item[1],
                -frequency[item[0]],
                item[0] not in TECH_KEYWORD_PRIORITY,
                item[0],
            ),
        )
        top_terms = [term for term, _ in scored_terms[: self.max_keywords]]

        # TF-IDF has ties in one-document extraction, so frequency keeps output stable and useful.
        return sorted(top_terms, key=lambda term: (-frequency[term], term))

    def _match_label(self, score: float) -> str:
        if score >= 80:
            return "Strong match"
        if score >= 60:
            return "Good match"
        if score >= 40:
            return "Partial match"
        return "Low match"

    def _recommendations(self, score: float, missing_keywords: list[str]) -> list[str]:
        recommendations: list[str] = []

        if missing_keywords:
            top_missing = ", ".join(missing_keywords[:6])
            recommendations.append(
                f"Add evidence for these job keywords where truthful: {top_missing}."
            )
        if score < 60:
            recommendations.append(
                "Rewrite the resume summary and project bullets to mirror the target role more closely."
            )
        if score < 80:
            recommendations.append(
                "Quantify project impact with metrics, scale, accuracy improvements, or performance gains."
            )

        recommendations.append(
            "Keep skills, project titles, and tools consistent with the wording used in the job description."
        )
        return recommendations
