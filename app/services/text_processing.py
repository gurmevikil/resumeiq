import io
import re
from pathlib import Path

from fastapi import UploadFile
from pypdf import PdfReader
from docx import Document

STOP_WORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "has",
    "have",
    "in",
    "is",
    "it",
    "of",
    "on",
    "or",
    "our",
    "that",
    "the",
    "their",
    "this",
    "to",
    "with",
    "you",
    "your",
}

SUPPORTED_EXTENSIONS = {".txt", ".pdf", ".docx"}


def clean_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9+#.\s-]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def tokenize(text: str) -> list[str]:
    cleaned = clean_text(text)
    raw_tokens = re.findall(r"[a-z0-9+#.]+", cleaned)
    tokens = [token.strip(".-") for token in raw_tokens]
    return [token for token in tokens if token not in STOP_WORDS and len(token) > 1]


def normalized_text(text: str) -> str:
    return " ".join(tokenize(text))


def word_count(text: str) -> int:
    return len(tokenize(text))


async def extract_text_from_upload(file: UploadFile) -> str:
    extension = Path(file.filename or "").suffix.lower()
    if extension not in SUPPORTED_EXTENSIONS:
        supported = ", ".join(sorted(SUPPORTED_EXTENSIONS))
        raise ValueError(f"Unsupported file type. Supported types: {supported}")

    content = await file.read()
    if not content:
        raise ValueError("Uploaded resume file is empty.")

    if extension == ".txt":
        return content.decode("utf-8", errors="ignore")
    if extension == ".pdf":
        return extract_text_from_pdf(content)
    return extract_text_from_docx(content)


def extract_text_from_pdf(content: bytes) -> str:
    reader = PdfReader(io.BytesIO(content))
    page_text = [page.extract_text() or "" for page in reader.pages]
    text = "\n".join(page_text).strip()
    if not text:
        raise ValueError("Could not extract text from PDF.")
    return text


def extract_text_from_docx(content: bytes) -> str:
    document = Document(io.BytesIO(content))
    paragraphs = [paragraph.text for paragraph in document.paragraphs]
    text = "\n".join(paragraphs).strip()
    if not text:
        raise ValueError("Could not extract text from DOCX.")
    return text
