from __future__ import annotations

from io import BytesIO

from docx import Document
from pypdf import PdfReader


SUPPORTED_EXTENSIONS: set[str] = {
    "pdf",
    "docx",
    "txt",
}


def get_file_extension(filename: str) -> str:
    return filename.rsplit(".", maxsplit=1)[-1].lower()


def extract_text_from_txt(file_bytes: bytes) -> str:
    return file_bytes.decode(
        "utf-8",
        errors="ignore",
    )


def extract_text_from_pdf(file_bytes: bytes) -> str:
    reader = PdfReader(BytesIO(file_bytes))

    pages: list[str] = []

    for page in reader.pages:
        text = page.extract_text() or ""
        pages.append(text)

    return "\n\n".join(pages).strip()


def extract_text_from_docx(file_bytes: bytes) -> str:
    document = Document(BytesIO(file_bytes))

    paragraphs: list[str] = [
        paragraph.text.strip()
        for paragraph in document.paragraphs
        if paragraph.text.strip()
    ]

    return "\n".join(paragraphs).strip()


def extract_text_from_uploaded_file(
    filename: str,
    file_bytes: bytes,
) -> str:
    extension = get_file_extension(filename)

    if extension not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            f"Unsupported file type: {extension}"
        )

    if extension == "pdf":
        return extract_text_from_pdf(file_bytes)

    if extension == "docx":
        return extract_text_from_docx(file_bytes)

    return extract_text_from_txt(file_bytes)