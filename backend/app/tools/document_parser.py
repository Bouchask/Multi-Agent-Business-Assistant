import os
from loguru import logger
import pypdf
import docx

class DocumentParserTool:
    @staticmethod
    def extract_text(file_path: str) -> str:
        if not os.path.exists(file_path):
            return ""
        ext = os.path.splitext(file_path)[1].lower()
        try:
            if ext == ".pdf":
                reader = pypdf.PdfReader(file_path)
                return "\n".join(page.extract_text() or "" for page in reader.pages)
            elif ext == ".docx":
                doc = docx.Document(file_path)
                return "\n".join(para.text for para in doc.paragraphs)
            elif ext == ".txt":
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    return f.read()
            else:
                return f"[Unsupported file type: {ext}]"
        except Exception as e:
            logger.error(f"Error parsing document {file_path}: {e}")
            return ""
