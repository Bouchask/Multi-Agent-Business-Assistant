from typing import Dict, Any, List, Optional
from loguru import logger
from backend.app.db.session import SessionLocal
from backend.app.models.meeting import Meeting

class DatabaseTool:
    """
    Structured Relational Database Audit Tool.
    Verifies SQL commits and record consistency, emitting structured JSON payloads exclusively.
    """
    @staticmethod
    def verify_meeting_record(title_keyword: str, date_str: Optional[str] = None) -> Dict[str, Any]:
        logger.info(f"💾 DATABASE TOOL: Verifying record persistence for keyword '{title_keyword}' on '{date_str}'")
        db = SessionLocal()
        found = []
        try:
            meetings = db.query(Meeting).all()
            for m in meetings:
                if title_keyword.lower() in str(m.title).lower() or title_keyword.lower() in str(m.description).lower() or "deleted_" in title_keyword:
                    if date_str and str(date_str) not in str(m.start_time) and str(date_str) != "All":
                        continue
                    found.append({
                        "id": m.id,
                        "title": m.title,
                        "start_time": m.start_time.strftime("%Y-%m-%d %H:%M:%S"),
                        "location_or_link": m.location_or_link
                    })
            return {
                "tool_name": "DatabaseTool",
                "success": True,
                "record_count": len(found),
                "verified_records": found
            }
        except Exception as e:
            logger.error(f"DatabaseTool query failure: {e}")
            return {"tool_name": "DatabaseTool", "success": False, "error": str(e)}
        finally:
            db.close()
