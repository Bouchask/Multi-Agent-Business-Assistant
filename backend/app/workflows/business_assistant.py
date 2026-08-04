from typing import Dict, Any, TypedDict, List, Optional
from loguru import logger
from langgraph.graph import StateGraph, END
from backend.app.agents import *
from backend.app.llm.client import llm_client

class AgentState(TypedDict):
    user_input: str
    next_agent: str
    response: str
    history: List[Dict[str, Any]]

def supervisor_node(state: AgentState) -> AgentState:
    logger.info("🤖 LANGGRAPH SUPERVISOR: Evaluating request & context to determine specialized agent...")
    chosen = supervisor_agent.route_request(state["user_input"], history=state.get("history"))
    logger.info(f"➡️ SUPERVISOR DECISION: Routing task to [{chosen}]")
    return {"user_input": state["user_input"], "next_agent": chosen, "response": "", "history": state.get("history", [])}

def research_node(state: AgentState) -> AgentState:
    res = research_agent.run(state["user_input"], history=state.get("history"))
    return {"user_input": state["user_input"], "next_agent": "RESEARCH", "response": res, "history": state.get("history", [])}

def email_node(state: AgentState) -> AgentState:
    res = email_agent.run(state["user_input"])
    return {"user_input": state["user_input"], "next_agent": "EMAIL", "response": res, "history": state.get("history", [])}

def scheduling_node(state: AgentState) -> AgentState:
    res = scheduling_agent.run(state["user_input"], history=state.get("history"))
    return {"user_input": state["user_input"], "next_agent": "SCHEDULING", "response": res, "history": state.get("history", [])}

def developer_node(state: AgentState) -> AgentState:
    res = developer_agent.run(state["user_input"])
    return {"user_input": state["user_input"], "next_agent": "DEVELOPER", "response": res, "history": state.get("history", [])}

def analytics_node(state: AgentState) -> AgentState:
    res = data_analyst_agent.run(state["user_input"])
    return {"user_input": state["user_input"], "next_agent": "ANALYTICS", "response": res, "history": state.get("history", [])}

def writer_node(state: AgentState) -> AgentState:
    res = content_writer_agent.run(state["user_input"])
    return {"user_input": state["user_input"], "next_agent": "WRITER", "response": res, "history": state.get("history", [])}

def knowledge_node(state: AgentState) -> AgentState:
    res = knowledge_agent.run(state["user_input"])
    return {"user_input": state["user_input"], "next_agent": "KNOWLEDGE", "response": res, "history": state.get("history", [])}

def translation_node(state: AgentState) -> AgentState:
    res = translation_agent.run(state["user_input"])
    return {"user_input": state["user_input"], "next_agent": "TRANSLATION", "response": res, "history": state.get("history", [])}

def ocr_file_node(state: AgentState) -> AgentState:
    res = ocr_file_agent.run(state["user_input"])
    return {"user_input": state["user_input"], "next_agent": "OCR_FILE", "response": res, "history": state.get("history", [])}

def vision_voice_node(state: AgentState) -> AgentState:
    res = vision_voice_agent.run(state["user_input"])
    return {"user_input": state["user_input"], "next_agent": "VISION_VOICE", "response": res, "history": state.get("history", [])}

def workflow_node(state: AgentState) -> AgentState:
    res = workflow_agent.run(state["user_input"])
    return {"user_input": state["user_input"], "next_agent": "WORKFLOW", "response": res, "history": state.get("history", [])}

def security_node(state: AgentState) -> AgentState:
    res = security_agent.run(state["user_input"])
    return {"user_input": state["user_input"], "next_agent": "SECURITY", "response": res, "history": state.get("history", [])}

def notification_node(state: AgentState) -> AgentState:
    res = notification_agent.run(state["user_input"])
    return {"user_input": state["user_input"], "next_agent": "NOTIFICATION", "response": res, "history": state.get("history", [])}

def general_node(state: AgentState) -> AgentState:
    context_str = ""
    if state.get("history"):
        last_msgs = state["history"][-4:]
        context_str = "Conversation Context:\n" + "\n".join([f"- {m.get('role', 'user')}: {m.get('content', '')}" for m in last_msgs]) + "\n\n"

    prompt = [
        {"role": "system", "content": "You are the Executive Supervisor AI Operating System. Provide a helpful, accurate, and professional response."},
        {"role": "user", "content": f"{context_str}User Instruction: {state['user_input']}"}
    ]
    res = llm_client.complete(messages=prompt)
    return {"user_input": state["user_input"], "next_agent": "GENERAL", "response": res.get("content", "How may I assist your business today?"), "history": state.get("history", [])}

def route_decision(state: AgentState) -> str:
    mapping = {
        "RESEARCH": "research",
        "EMAIL": "email",
        "SCHEDULING": "scheduling",
        "DEVELOPER": "developer",
        "ANALYTICS": "analytics",
        "WRITER": "writer",
        "KNOWLEDGE": "knowledge",
        "TRANSLATION": "translation",
        "OCR_FILE": "ocr_file",
        "VISION_VOICE": "vision_voice",
        "WORKFLOW": "workflow",
        "SECURITY": "security",
        "NOTIFICATION": "notification",
        "GENERAL": "general"
    }
    return mapping.get(state.get("next_agent", "GENERAL"), "general")

def build_workflow():
    workflow = StateGraph(AgentState)
    
    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("research", research_node)
    workflow.add_node("email", email_node)
    workflow.add_node("scheduling", scheduling_node)
    workflow.add_node("developer", developer_node)
    workflow.add_node("analytics", analytics_node)
    workflow.add_node("writer", writer_node)
    workflow.add_node("knowledge", knowledge_node)
    workflow.add_node("translation", translation_node)
    workflow.add_node("ocr_file", ocr_file_node)
    workflow.add_node("vision_voice", vision_voice_node)
    workflow.add_node("workflow", workflow_node)
    workflow.add_node("security", security_node)
    workflow.add_node("notification", notification_node)
    workflow.add_node("general", general_node)

    workflow.set_entry_point("supervisor")
    workflow.add_conditional_edges("supervisor", route_decision)

    all_targets = [
        "research", "email", "scheduling", "developer", "analytics", "writer",
        "knowledge", "translation", "ocr_file", "vision_voice", "workflow",
        "security", "notification", "general"
    ]
    for node_name in all_targets:
        workflow.add_edge(node_name, END)

    return workflow.compile()

multi_agent_app = build_workflow()

class MultiAgentOrchestrator:
    @staticmethod
    def execute(user_input: str, history: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        logger.info(f"\n🚀 STARTING LANGGRAPH ORCHESTRATED WORKFLOW for query: '{user_input}'")
        initial_state: AgentState = {"user_input": user_input, "next_agent": "GENERAL", "response": "", "history": history or []}
        result = multi_agent_app.invoke(initial_state)
        return {
            "success": True,
            "agent_triggered": result.get("next_agent", "GENERAL") + " AGENT",
            "response": result.get("response", "")
        }
