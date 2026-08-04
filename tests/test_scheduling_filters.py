import os
import sys
import unittest
import datetime
from loguru import logger

# Ensure project root is in python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app.tools.calendar_tool import CalendarTool
from backend.app.db.session import SessionLocal, engine
from backend.app.models.meeting import Meeting
from backend.app.models.base import StructuredMission, DomainType, ToolExecutionResult
from backend.app.agents.verification.execution_verifier import ExecutionVerifierAgent
from backend.app.agents.reporting.executive_reporter import ExecutiveReporterAgent
from backend.app.core.exceptions import VerificationFailedError
from backend.app.workflows.business_assistant import MultiAgentOrchestrator

class TestSchedulingFilters(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        logger.info("🧪 SETTING UP TEST SUITE: PRESERVED MISSION PARAMETERS & FILTERS")
        db = SessionLocal()
        try:
            # Clear existing DB meetings for clean deterministic testing of the database source
            db.query(Meeting).delete()
            db.commit()

            # Insert known sample meetings across dates and participants into SQLite
            CalendarTool.add_meeting("Meeting with dev Ayoub", "2026-08-04", "10:00:00", "Project discussion")
            CalendarTool.add_meeting("Meeting with Ayoub", "2026-08-24", "09:00:00", "Architecture review")
            CalendarTool.add_meeting("Meeting with Dr. Yahya for gestion labo", "2026-08-13", "10:00:00", "Lab management")
            CalendarTool.add_meeting("Meeting with Dr. Hamza - MVC Discussion", "2026-09-10", "10:00:00", "September sync")
            logger.info("✅ Inserted 4 reference test meetings into SQLite DB.")
        except Exception as e:
            logger.error(f"Error initializing test records: {e}")
        finally:
            db.close()

    def test_01_meetings_with_ayoub(self):
        logger.info("🧪 TEST 1: 'Meetings with Ayoub'")
        # Test exact DB filtering
        res_db = CalendarTool.list_meetings(participant="Ayoub", source="database")
        self.assertEqual(len(res_db.get("events", [])), 2, "Expected exactly 2 Ayoub meetings in SQLite database")
        
        # Test across all sources (DB + Google Calendar)
        res_all = CalendarTool.list_meetings(participant="Ayoub")
        self.assertTrue(res_all.get("success"))
        events = res_all.get("events", [])
        self.assertTrue(len(events) >= 2, "Must find at least the 2 DB meetings plus any matching Google Calendar events")
        for e in events:
            text_block = (e["summary"] + " " + e.get("description", "")).lower()
            self.assertIn("ayoub", text_block, f"Returned event {e['summary']} failed filter compliance")
            self.assertNotIn("yahya", text_block, f"Unrelated participant Dr. Yahya leaked into Ayoub filter")

    def test_02_meetings_with_dr_yahya(self):
        logger.info("🧪 TEST 2: 'Meetings with Dr. Yahya'")
        res_db = CalendarTool.list_meetings(participant="Dr. Yahya", source="database")
        self.assertEqual(len(res_db.get("events", [])), 1, "Expected exactly 1 Dr. Yahya meeting in SQLite database")
        
        res_all = CalendarTool.list_meetings(participant="Dr. Yahya")
        self.assertTrue(res_all.get("success"))
        for e in res_all.get("events", []):
            self.assertIn("yahya", (e["summary"] + " " + e.get("description", "")).lower())

    def test_03_meetings_in_august(self):
        logger.info("🧪 TEST 3: 'Meetings in August'")
        res_num = CalendarTool.list_meetings(month=8, year=2026, source="database")
        res_str = CalendarTool.list_meetings(month="August", year=2026, source="database")
        self.assertEqual(len(res_num["events"]), 3, "Should find exactly 3 August meetings in database")
        self.assertEqual(len(res_str["events"]), 3, "String month 'August' should map correctly to month 8")
        
        res_all = CalendarTool.list_meetings(month=8, year=2026)
        for e in res_all["events"]:
            self.assertIn("2026-08-", e["start"])
            self.assertNotIn("hamza", e["summary"].lower(), "September meeting must never appear in August query")

    def test_04_meetings_on_august_24(self):
        logger.info("🧪 TEST 4: 'Meetings on August 24'")
        res_date_iso = CalendarTool.list_meetings(date="2026-08-24", source="database")
        self.assertEqual(len(res_date_iso["events"]), 1)
        self.assertIn("2026-08-24", res_date_iso["events"][0]["start"])
        
        res_all = CalendarTool.list_meetings(date="2026-08-24")
        for e in res_all["events"]:
            self.assertIn("2026-08-24", e["start"])

    def test_05_no_matching_meetings(self):
        logger.info("🧪 TEST 5: 'No matching meetings'")
        res = CalendarTool.list_meetings(participant="Nonexistent Person 99")
        self.assertTrue(res["success"])
        self.assertEqual(res["count"], 0)
        self.assertEqual(res["events"], [])

    def test_06_multiple_filters(self):
        logger.info("🧪 TEST 6: Multiple filters - Combined participant and month")
        res_match = CalendarTool.list_meetings(participant="Ayoub", month=8, year=2026, source="database")
        self.assertEqual(len(res_match["events"]), 2)
        
        res_no_match = CalendarTool.list_meetings(participant="Ayoub", month=9, year=2026, source="database")
        self.assertEqual(len(res_no_match["events"]), 0, "Ayoub has no meetings in September")

    def test_07_database_only(self):
        logger.info("🧪 TEST 7: 'Database only'")
        res = CalendarTool.list_meetings(source="database")
        self.assertTrue(len(res["events"]) >= 4)
        for e in res["events"]:
            self.assertEqual(e.get("source"), "database")
            self.assertTrue(e["summary"].startswith("[DB Record]"))

    def test_08_google_calendar_only(self):
        logger.info("🧪 TEST 8: 'Google Calendar only'")
        res = CalendarTool.list_meetings(source="google_calendar")
        for e in res["events"]:
            self.assertEqual(e.get("source"), "google_calendar")

    def test_09_verification_failure_on_mismatch(self):
        logger.info("🧪 TEST 9: Verifier audit raises error if filters are violated")
        mission = StructuredMission(intent="QUERY", filters={"participant": "Ayoub"})
        # Simulate a bug where tool returned a meeting with Dr. Yahya instead of Ayoub
        fake_tool_res = [ToolExecutionResult(
            tool_name="CalendarTool", 
            success=True, 
            action_performed="list_meetings", 
            data={"events": [{"summary": "[DB Record] Meeting with Dr. Yahya", "start": "2026-08-13 10:00:00"}]}
        )]
        with self.assertRaises(VerificationFailedError):
            ExecutionVerifierAgent.verify(mission, fake_tool_res)
            
    def test_10_end_to_end_pipeline_filter_preservation(self):
        logger.info("🧪 TEST 10: End-to-End Orchestrator Pipeline Preservation")
        
        # Test query for Ayoub via execute()
        res_ayoub = MultiAgentOrchestrator.execute("List meetings with Ayoub")
        res_md = res_ayoub.get("reply", "")
        self.assertIn("Ayoub", res_md)
        self.assertNotIn("Yahya", res_md, "End-to-End report must never mention unrelated meetings!")
        self.assertNotIn("Hamza", res_md, "End-to-End report must never mention unrelated meetings!")
        
        # Test empty matches return clean mandated text
        res_empty = MultiAgentOrchestrator.execute("List meetings with Elon Musk")
        self.assertIn("No meetings matching your request were found.", res_empty.get("reply", ""))

    def test_11_insert_meeting_with_pre_execution_audit(self):
        logger.info("🧪 TEST 11: Insert Meeting with Pre-Execution Availability Audit")
        res = MultiAgentOrchestrator.execute("insert meet with ayoub in 24-08-2026")
        self.assertTrue(res.get("success"), "Orchestration must complete successfully without verification exceptions")
        self.assertNotIn("VerificationFailedError", res.get("reply", ""))
        self.assertNotIn("Verification failed", res.get("reply", ""))

if __name__ == "__main__":
    unittest.main()
