from __future__ import annotations

from typing import TypedDict, Optional, Dict, Any
import asyncio

from langgraph.graph import StateGraph, END

from agents.ceo import CEOAgent
from agents.research import ResearchAgent
from agents.writer import WriterAgent
from agents.developer import DeveloperAgent
from agents.automation import AutomationAgent
from agents.confidence import ConfidenceAgent
from agents.reviewer import ReviewerAgent
from utils import format_email_content


class PipelineState(TypedDict, total=False):
    session_id: str
    goal: str
    email: Optional[str]
    plan: Dict[str, Any]
    research: Dict[str, Any]
    developer: Dict[str, Any]
    writer: Dict[str, Any]
    confidence: Dict[str, Any]
    reviewer: Dict[str, Any]


class LangGraphOrchestrator:
    """Graph-based multi-agent pipeline using LangGraph.

    Simplified flow: CEO+Research -> Developer -> Writer
    (No confidence/hallucination stage)
    """

    def __init__(self, memory):
        self.memory = memory
        # Initialize agents first
        self.ceo = CEOAgent("CEO", memory)
        self.research = ResearchAgent("Research", memory)
        self.writer = WriterAgent("Writer", memory)
        self.developer = DeveloperAgent("Developer", memory)
        self.automation = AutomationAgent("Automation", memory)
        self.confidence = ConfidenceAgent("Confidence", memory)
        self.reviewer = ReviewerAgent("Reviewer", memory)
        # Build graph once
        self.app = self._build_graph()

    def _build_graph(self):
        graph = StateGraph(PipelineState)

        async def node_ceo_and_research(state: PipelineState) -> PipelineState:
            """Combined CEO + Research node (1 API call instead of 2)."""
            goal = str(state.get("goal", "")).strip()
            
            # If this is a retry iteration, include hallucination issues
            conf = state.get("confidence") or {}
            issues = conf.get("hallucination_issues") or []
            if issues:
                goal = (
                    f"{goal}\n\n"
                    f"⚠️ Previous hallucination issues to address:\n"
                    + "\n".join(f"- {x}" for x in issues)
                )
            
            # Use API key 1 (index 0)
            combined = await self.ceo.create_plan_and_research(goal, key_index=0)
            plan = {"goal": combined.get("goal"), "tasks": combined.get("tasks", [])}
            research = combined.get("research", {})
            await self.memory.save_plan(state["session_id"], plan)
            await self.memory.save_research(state["session_id"], research)
            return {"plan": plan, "research": research}

        async def node_validation(state: PipelineState) -> PipelineState:
            # Delay between transitions
            await asyncio.sleep(2)
            doc_content = ((state.get("writer") or {}).get("document", ""))
            # Use Key 1 only for combined confidence + hallucination
            combined = await self.confidence.evaluate_and_store(state["session_id"], doc_content, key_index=0)
            return {"confidence": combined}

        async def node_developer(state: PipelineState) -> PipelineState:
            # Delay between transitions
            await asyncio.sleep(2)
            tasks = (state.get("plan", {}) or {}).get("tasks", [])
            dev_task = next((t.get("description") for t in tasks if t.get("assigned_agent") == "Developer"), None)
            instructions = dev_task or "Create a concise technical outline or mermaid diagram."
            if state.get("research"):
                instructions = (
                    f"{instructions}\n\nContext from Research (use if helpful):\n{state['research']}"
                )
            # Use API key 2 (index 1)
            dev_result = await self.developer.generate_diagram(instructions, key_index=1)
            return {"developer": dev_result}

        async def node_writer(state: PipelineState) -> PipelineState:
            # Delay between transitions
            await asyncio.sleep(2)
            tasks = (state.get("plan", {}) or {}).get("tasks", [])
            writer_task = next((t.get("description") for t in tasks if t.get("assigned_agent") == "Writer"), None)
            brief = (writer_task or "Draft a final response for the user.").strip()
            brief = (
                f"User goal:\n{state.get('goal','')}\n\n"
                f"Writing task:\n{brief}\n\n"
                f"Research output (authoritative context):\n{state.get('research')}\n\n"
                f"Developer output (technical artifacts):\n{state.get('developer')}\n"
            )
            # Use API key 3 (index 2)
            doc = await self.writer.write_document(brief, key_index=2)
            await self.memory.save_document(state["session_id"], doc)
            return {"writer": doc}

        async def node_reviewer(state: PipelineState) -> PipelineState:
            """Reviewer node to fix issues identified by confidence agent."""
            await asyncio.sleep(2)
            doc_content = ((state.get("writer") or {}).get("document", ""))
            conf = state.get("confidence") or {}
            issues = conf.get("hallucination_issues") or []
            
            # Use API key 2 (index 1)
            revised_doc = await self.reviewer.repair(
                original_document=doc_content,
                detected_issues=issues,
                user_revision_instruction="Fix the identified issues",
                constraints=None,
                key_index=1
            )
            await self.memory.save_document(state["session_id"], revised_doc)
            return {"reviewer": revised_doc, "writer": revised_doc}

        # Register nodes
        graph.add_node("ceo_and_research", node_ceo_and_research)
        graph.add_node("developer", node_developer)
        graph.add_node("writer", node_writer)
        graph.add_node("validation", node_validation)
        graph.add_node("reviewer", node_reviewer)

        # Linear handoff
        graph.add_edge("ceo_and_research", "developer")
        graph.add_edge("developer", "writer")
        graph.add_edge("writer", "validation")
        graph.add_edge("validation", "reviewer")
        graph.add_edge("reviewer", END)

        graph.set_entry_point("ceo_and_research")
        return graph.compile()

    async def run(self, goal: str, email_target: Optional[str] = None) -> Dict[str, Any]:
        # Create session and initial state
        session_id = await self.memory.create_session(goal, email_target)
        initial: PipelineState = {"session_id": session_id, "goal": goal, "email": email_target}

        # Execute the graph (async)
        final_state: PipelineState = await self.app.ainvoke(initial)

        # Print confidence & hallucination metrics at the end (if available)
        conf = final_state.get("confidence") or {}
        try:
            cs = conf.get("confidence_score")
            hr = conf.get("hallucination_risk")
            hrs = conf.get("hallucination_risk_score")
            if cs is not None or hr is not None or hrs is not None:
                print("\n--- Quality Metrics ---")
                print(f"Confidence Score: {cs}")
                print(f"Hallucination Risk: {hr} ({hrs})")
                issues = conf.get("hallucination_issues") or []
                if issues:
                    print("Issues:")
                    for i, iss in enumerate(issues, 1):
                        print(f"  {i}. {iss}")
        except Exception:
            pass

        # Optional email send (single final email only)
        email_result = None
        if email_target:
            try:
                subject = f"Final Draft: {goal}".strip()
                body = format_email_content(
                    ((final_state.get("writer") or {}).get("document", "")),
                    confidence=final_state.get("confidence")
                )
                email_result = await self.automation.send_output(email_target, subject, body)
                await self.memory.save_actions(
                    session_id,
                    {
                        "type": "email_send",
                        "to": email_target,
                        "subject": subject,
                        "result": email_result,
                    },
                )
            except Exception as exc:
                email_result = {"ok": False, "error": str(exc)}
                await self.memory.save_actions(
                    session_id,
                    {
                        "type": "email_send",
                        "to": email_target,
                        "subject": f"Final Draft: {goal}".strip(),
                        "result": email_result,
                    },
                )

        return {
            "session_id": session_id,
            "plan": final_state.get("plan"),
            "handoff": {
                "research": final_state.get("research"),
                "developer": final_state.get("developer"),
                "writer": final_state.get("writer"),
                "reviewer": final_state.get("reviewer"),
            },
            "final": final_state.get("reviewer") or final_state.get("writer"),
            "email": {
                "requested": bool(email_target),
                "to": email_target,
                "result": email_result,
            },
            # Place confidence at the end so it appears last in JSON
            "confidence": final_state.get("confidence"),
        }
