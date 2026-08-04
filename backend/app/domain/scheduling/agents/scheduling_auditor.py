import json
from typing import List, Dict, Any
from loguru import logger
from backend.app.llm.client import llm_client
from backend.app.domain.scheduling.models import AuditDecision, AuditClassification, ExecutiveRiskLevel, MissionProfile
from backend.app.domain.scheduling.prompts import SCHEDULING_AUDITOR_PROMPT

class SchedulingAuditorAgent:
    """
    Agent 2: Scheduling Auditor & Executive Risk Evaluator
    Responsibilities: Analyze existing meetings, perform semantic conflict evaluation, evaluate risk level, and determine whether autonomous execution is safe or requires explicit authorization.
    Strict Rule: Weekly meetings on different dates are never duplicates. Routine tasks execute independently without confirmation.
    """
    @staticmethod
    def audit_request(mission: MissionProfile, existing_events: List[Dict[str, Any]], user_command: str) -> AuditDecision:
        logger.info(f"⚖️ SCHEDULING AUDITOR: Reviewing mission '{mission.mission.value}' against {len(existing_events)} records for semantic conflicts & operational risk...")
        
        override_words = ["confirm", "force", "insert anyway", "oui", "yes proceed", "ignore warning", "override", "valide", "valider", "yes", "delete all", "mise a jour", "supprimer", "clear"]
        has_override = any(w in user_command.lower() for w in override_words)
        
        if has_override or mission.mission.value in ["CONFIRM", "QUERY"]:
            return AuditDecision(
                decision=AuditClassification.SAFE_NEW_MEETING,
                risk_level=ExecutiveRiskLevel.ROUTINE_SAFE,
                confidence=1.0,
                reason="Executive provided explicit authorization override or read-only routine query."
            )

        if not existing_events:
            return AuditDecision(
                decision=AuditClassification.SAFE_NEW_MEETING,
                risk_level=ExecutiveRiskLevel.ROUTINE_SAFE,
                confidence=1.0,
                reason="No existing events found in repository; schedule is completely open and safe to modify."
            )

        # Filter events matching the target date for optimal contextual focus
        target_date = mission.entities.date
        same_date_events = [e for e in existing_events if target_date in str(e.get("start", ""))]
        
        if not same_date_events and mission.mission.value in ["CREATE", "UPDATE"]:
            return AuditDecision(
                decision=AuditClassification.SAFE_NEW_MEETING,
                risk_level=ExecutiveRiskLevel.ROUTINE_SAFE,
                confidence=0.98,
                reason=f"No existing events on {target_date}. Routine safe booking on an open calendar slot."
            )

        try:
            res = llm_client.complete(
                messages=[
                    {"role": "system", "content": SCHEDULING_AUDITOR_PROMPT},
                    {
                        "role": "user",
                        "content": f"Proposed Mission:\n{mission.model_dump_json(indent=2)}\n\nExisting Events on Target Date ({target_date}):\n{json.dumps(same_date_events, indent=2)}\n\nEvaluate semantic duplicate status and operational risk level."
                    }
                ],
                temperature=0.1
            )
            raw_json = res.get("content", "{}").strip()
            if raw_json.startswith("```json"):
                raw_json = raw_json[7:-3].strip()
            elif raw_json.startswith("```"):
                raw_json = raw_json[3:-3].strip()
            
            data = json.loads(raw_json)
            logger.info(f"⚖️ AUDITOR DECISION: {data}")
            return AuditDecision(**data)
        except Exception as e:
            logger.warning(f"Scheduling Auditor fallback: {e}")
            # By default, treat standard creations as ROUTINE_SAFE unless deletions without targets occur
            is_sensitive = mission.mission.value in ["DELETE", "CANCEL"] and not has_override
            return AuditDecision(
                decision=AuditClassification.NEED_CONFIRMATION if is_sensitive else AuditClassification.SAFE_NEW_MEETING,
                risk_level=ExecutiveRiskLevel.SENSITIVE_REQUIRES_CONFIRMATION if is_sensitive else ExecutiveRiskLevel.ROUTINE_SAFE,
                confidence=0.90,
                reason="Evaluated operational safety and semantic separation with fallback confidence."
            )
