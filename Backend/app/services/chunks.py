import re
from typing import List, Dict


SECTION_PATTERNS = [
    "summary",
    "professional summary",
    "profile",
    "objective",
    "skills",
    "technical skills",
    "core competencies",
    "experience",
    "work experience",
    "employment history",
    "projects",
    "personal projects",
    "academic projects",
    "education",
    "certifications",
    "achievements",
    "internships",
    "languages",
    "interests"
]


def clean_text(text: str) -> str:
    text = text.replace("\r", "\n")
    text = re.sub(r"\n{2,}", "\n\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()


def normalize_heading(line: str) -> str:
    return re.sub(r"[^a-z ]", "", line.lower()).strip()


def split_into_sections(text: str) -> List[Dict]:
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    sections = []

    current_heading = "general"
    current_content = []

    for line in lines:
        normalized = normalize_heading(line)

        if normalized in SECTION_PATTERNS:
            if current_content:
                sections.append({
                    "section": current_heading,
                    "content": "\n".join(current_content).strip()
                })
            current_heading = normalized
            current_content = []
        else:
            current_content.append(line)

    if current_content:
        sections.append({
            "section": current_heading,
            "content": "\n".join(current_content).strip()
        })

    return sections


def split_large_text(text: str, chunk_size: int = 500, overlap: int = 100) -> List[str]:
    if len(text) <= chunk_size:
        return [text]

    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start += chunk_size - overlap

    return chunks


def chunk_resume_text(text: str, source_filename: str = "resume.pdf") -> List[Dict]:
    cleaned = clean_text(text)
    sections = split_into_sections(cleaned)

    final_chunks = []
    chunk_id = 1

    for section in sections:
        section_name = section["section"]
        section_text = section["content"]

        split_chunks = split_large_text(section_text, chunk_size=500, overlap=100)

        for part in split_chunks:
            final_chunks.append({
                "chunk_id": chunk_id,
                "section": section_name,
                "text": part,
                "source": source_filename
            })
            chunk_id += 1

    return final_chunks