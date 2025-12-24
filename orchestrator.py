# from agents.ceo import CEOAgent
# from agents.research import ResearchAgent
# from agents.writer import WriterAgent
# from agents.developer import DeveloperAgent
# from agents.automation import AutomationAgent
# from agents.reviewer import ReviewerAgent
# from agents.confidence import ConfidenceAgent
# from utils import format_email_content
# import asyncio

# class Orchestrator:
#     def __init__(self, memory):
#         self.ceo = CEOAgent("CEO", memory)
#         self.research = ResearchAgent("Research", memory)
#         self.writer = WriterAgent("Writer", memory)
#         self.developer = DeveloperAgent("Developer", memory)
#         self.automation = AutomationAgent("Automation", memory)
#         self.reviewer = ReviewerAgent("Reviewer", memory)
#         self.confidence = ConfidenceAgent("Confidence", memory)
#         self.memory = memory

#     async def run(self, goal, email_target):
#     # 🔹 Create session
#         session_id = await self.memory.create_session(goal, email_target)

#         # 🔹 CEO plan
#         plan = await self.ceo.create_plan(goal)
#         await self.memory.save_plan(session_id, plan)

#         results = []

#         # split task by agent
#         research_tasks = []
#         developer_tasks = []
#         writer_tasks = []

#         for task in plan.get("tasks", []):
#             agent = task.get("assigned_agent")
#             desc = task.get("description")

#             if agent == "Research":
#                 # research = await self.research.run_research(desc)
#                 # await self.memory.save_research(session_id, research)
#                 research_tasks.append(desc)

#             elif agent == "Developer":
#                 # dev_result = await self.developer.generate_diagram(desc)
#                 developer_tasks.append(desc)
            
#             elif agent == "Writer":
#                 writer_tasks.append(desc)


#         # -----------------------------
#         # Parallel execution
#         # -----------------------------

#         async def run_research():
#             output = []
#             for desc in research_tasks:
#                 research = await self.research.run_research(desc)
#                 await self.memory.save_research(session_id, research)
#                 output.append(research)
#             return output

#         async def run_developer():
#             output = []
#             for desc in developer_tasks:
#                 dev_result = await self.developer.generate_diagram(desc)
#                 output.append(dev_result)
#             return output
        
#         research_results = await run_research()
#         await asyncio.sleep(1)   # small pause
#         dev_results = await run_developer()

#         results.extend(research_results)
#         results.extend(dev_results)

#         # -----------------------------
#         # 5️⃣ Writer + Reflection
#         # -----------------------------
#         if writer_tasks:
#             brief = f"""
#             {writer_tasks}

#             Use this research:
#             {research_results}

#             Use these diagrams / outputs:
#             {dev_results}
#             """

#             doc = await self.writer.write_document(brief)
#             await self.memory.save_document(session_id, doc)

#             review = await self.reviewer.review(doc["document"])

#             if review["status"] == "REVISE":
#                 improved_brief = f"""
#                 Improve the document using this feedback:

#                 Feedback:
#                 {review["feedback"]}

#                 Original Document:
#                 {doc["document"]}
#                 """
#                 doc = await self.writer.write_document(improved_brief)
#                 await self.memory.save_document(session_id, doc)

#             # -----------------------------
#             # 🧠 Confidence & Hallucination Check
#             # -----------------------------
#             confidence_report = await self.confidence.evaluate(doc["document"])
#             await self.memory.save_actions(session_id, {
#                 "type": "confidence_report",
#                 "data": confidence_report
#             })

#             # 🔁 Auto-revise if risk is HIGH
#             if confidence_report["verdict"] == "REVISE":
#                 safety_brief = f"""
#                 Reduce hallucinations and unsupported claims.
#                 Improve factual grounding using available research only.

#                 Issues:
#                 {confidence_report["issues"]}

#                 Document:
#                 {doc["document"]}
#                 """

#                 doc = await self.writer.write_document(safety_brief)
#                 await self.memory.save_document(session_id, doc)

#             final_doc = doc
#             results.append({
#                 "document": final_doc,
#                 "confidence": confidence_report
#             })





#         # Send ONE final email with the completed work
#         latest_doc = await self.memory.get_latest_document(session_id)
#         if latest_doc:
#             email_content = format_email_content(latest_doc.get("document", "Work completed"))
#             sent = await self.automation.send_output(
#                 email_target,
#                 f"Final Draft: {plan.get('goal', 'Your Request')}",
#                 email_content
#             )
#             await self.memory.save_actions(session_id, sent)
#             results.append({
#                 "email_sent": True,
#                 "formatted_output": email_content,
#                 "details": sent
#             })

#         return {
#             "session_id": session_id,
#             "plan": plan,
#             "results": results
#         }


# -----------------------------------------------------------------------------


from agents.ceo import CEOAgent
from agents.research import ResearchAgent
from agents.writer import WriterAgent
from agents.developer import DeveloperAgent
from agents.automation import AutomationAgent
from agents.confidence import ConfidenceAgent

from utils import format_email_content


class Orchestrator:
    """Multi-agent pipeline: CEO -> Research -> Developer -> Writer.

    This orchestrator is intentionally sequential to enforce handoff order:
    - CEO produces one task per agent
    - Research executes first
    - Developer uses research output to create technical artifacts
    - Writer uses research + developer output to draft the final response

    Email sending is intentionally not performed.
    """

    def __init__(self, memory):
        self.ceo = CEOAgent("CEO", memory)
        self.research = ResearchAgent("Research", memory)
        self.writer = WriterAgent("Writer", memory)
        self.developer = DeveloperAgent("Developer", memory)
        self.automation = AutomationAgent("Automation", memory)
        self.confidence = ConfidenceAgent("Confidence", memory)
        self.memory = memory

    async def run(self, goal: str, email_target: str | None = None):
        # 1) Create session (email is optional and not used for sending)
        session_id = await self.memory.create_session(goal, email_target)

        # 2) CEO handoff plan: exactly Research -> Developer -> Writer
        plan = await self.ceo.create_plan(goal)
        await self.memory.save_plan(session_id, plan)

        # 3) Execute in the fixed order
        tasks = plan.get("tasks", []) or []
        research_task = next((t.get("description") for t in tasks if t.get("assigned_agent") == "Research"), None)
        developer_task = next((t.get("description") for t in tasks if t.get("assigned_agent") == "Developer"), None)
        writer_task = next((t.get("description") for t in tasks if t.get("assigned_agent") == "Writer"), None)

        research_result = None
        if research_task:
            research_result = await self.research.run_research(str(research_task))
            await self.memory.save_research(session_id, research_result)

        developer_result = None
        if developer_task:
            dev_instructions = str(developer_task)
            if research_result:
                dev_instructions = (
                    f"{dev_instructions}\n\n"
                    f"Context from Research (use if helpful):\n{research_result}"
                )
            developer_result = await self.developer.generate_diagram(dev_instructions)

        brief = (writer_task or "Draft a final response for the user.").strip()
        brief = (
            f"User goal:\n{goal}\n\n"
            f"Writing task:\n{brief}\n\n"
            f"Research output (authoritative context):\n{research_result}\n\n"
            f"Developer output (technical artifacts):\n{developer_result}\n"
        )
        final_doc = await self.writer.write_document(brief)
        await self.memory.save_document(session_id, final_doc)

        # 4) Calculate and store confidence score (no rewrite/regeneration)
        confidence_result = None
        try:
            confidence_result = await self.confidence.evaluate_and_store(
                session_id,
                (final_doc or {}).get("document", ""),
            )
        except Exception:
            confidence_result = None

        # 5) Optional: send ONE email with the final draft only.
        email_result = None
        if email_target:
            try:
                subject = f"Final Draft: {goal}".strip()
                body = format_email_content((final_doc or {}).get("document", ""))
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
            "plan": plan,
            "handoff": {
                "research": research_result,
                "developer": developer_result,
                "writer": final_doc,
            },
            "final": final_doc,
            "confidence": confidence_result,
            "email": {
                "requested": bool(email_target),
                "to": email_target,
                "result": email_result,
            },
        }

    async def resume(self, session_id: str):
        """Compatibility endpoint for the existing /approve API.

        Re-runs Writer using the latest saved plan + saved research.
        """
        plan = await self.memory.get_latest_plan(session_id)
        if not plan:
            return {
                "session_id": session_id,
                "status": "ERROR",
                "message": "No plan found for session. Cannot resume.",
            }

        research_results = await self.memory.get_research(session_id)
        tasks = plan.get("tasks", []) or []
        writer_task = next((t.get("description") for t in tasks if t.get("assigned_agent") == "Writer"), None)
        developer_task = next((t.get("description") for t in tasks if t.get("assigned_agent") == "Developer"), None)

        developer_result = None
        if developer_task:
            dev_instructions = str(developer_task)
            if research_results:
                dev_instructions = f"{dev_instructions}\n\nContext from Research:\n{research_results}"
            developer_result = await self.developer.generate_diagram(dev_instructions)

        brief = (
            f"Writing task:\n{(writer_task or 'Draft the final response.')}\n\n"
            f"Research output:\n{research_results}\n\n"
            f"Developer output:\n{developer_result}\n"
        )
        final_doc = await self.writer.write_document(brief)
        await self.memory.save_document(session_id, final_doc)

        return {
            "session_id": session_id,
            "plan": plan,
            "handoff": {
                "research": research_results,
                "developer": developer_result,
                "writer": final_doc,
            },
            "final": final_doc,
        }
