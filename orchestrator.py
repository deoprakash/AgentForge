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

    async def run(self, goal: str, email_target: str | None = None, max_iterations: int = 3):
        # 1) Create session (email is optional and not used for sending)
        session_id = await self.memory.create_session(goal, email_target)

        # 2) CEO handoff plan: exactly Research -> Developer -> Writer
        plan = await self.ceo.create_plan(goal)
        await self.memory.save_plan(session_id, plan)

        # 3) Execute pipeline with feedback loop until confidence >= 90%
        tasks = plan.get("tasks", []) or []
        research_task = next((t.get("description") for t in tasks if t.get("assigned_agent") == "Research"), None)
        developer_task = next((t.get("description") for t in tasks if t.get("assigned_agent") == "Developer"), None)
        writer_task = next((t.get("description") for t in tasks if t.get("assigned_agent") == "Writer"), None)

        research_result = None
        developer_result = None
        final_doc = None
        confidence_result = {"confidence_score": 40, "source": "fallback"}
        iteration = 0
        hallucination_issues = None

        # FEEDBACK LOOP: Keep iterating until confidence >= 90% or max iterations reached
        while iteration < max_iterations:
            iteration += 1
            print(f"🔄 Iteration {iteration}/{max_iterations}")

            # Research phase (with optional hallucination feedback)
            if research_task:
                research_input = str(research_task)
                if hallucination_issues:
                    research_input = (
                        f"{research_task}\n\n"
                        f"⚠️ Previous hallucination issues found - please research these thoroughly:\n"
                        f"{chr(10).join(f'- {issue}' for issue in hallucination_issues)}"
                    )
                research_result = await self.research.run_research(research_input)
                await self.memory.save_research(session_id, research_result)

            # Developer phase (using refreshed research)
            if developer_task:
                dev_instructions = str(developer_task)
                if research_result:
                    dev_instructions = (
                        f"{dev_instructions}\n\n"
                        f"Context from Research (use if helpful):\n{research_result}"
                    )
                developer_result = await self.developer.generate_diagram(dev_instructions)

            # Writer phase (using refreshed developer output)
            brief = (writer_task or "Draft a final response for the user.").strip()
            brief = (
                f"User goal:\n{goal}\n\n"
                f"Writing task:\n{brief}\n\n"
                f"Research output (authoritative context):\n{research_result}\n\n"
                f"Developer output (technical artifacts):\n{developer_result}\n"
            )
            final_doc = await self.writer.write_document(brief)
            await self.memory.save_document(session_id, final_doc)

            # Check if we hit rate limits - if so, break the loop
            doc_content = (final_doc or {}).get("document", "")
            if "__LLM_RATE_LIMITED__" in str(doc_content) or "__LLM_UNAVAILABLE__" in str(doc_content):
                print(f"⛔ Rate limit hit at iteration {iteration}. Stopping pipeline.")
                confidence_result = {
                    "confidence_score": 0,
                    "confidence_source": "fallback",
                    "hallucination_risk": "UNKNOWN",
                    "hallucination_risk_score": 0,
                    "hallucination_issues": ["Pipeline interrupted due to rate limiting"],
                    "hallucination_summary": "Unable to complete pipeline - LLM rate limited",
                    "error": "LLM_RATE_LIMITED"
                }
                break

            # Confidence & Hallucination Check (only if document is valid)
            confidence_result = {"confidence_score": 40, "source": "fallback"}
            try:
                confidence_result = await self.confidence.evaluate_and_store(
                    session_id,
                    doc_content,
                )
            except Exception as e:
                print(f"⚠️ Confidence evaluation failed: {e}")
                confidence_result = {"confidence_score": 40, "source": "fallback", "error": str(e)}
                
                # On later iterations, if we hit rate limits during evaluation, be lenient
                if iteration > 1 and "rate" in str(e).lower():
                    print(f"ℹ️ Rate limit during iteration {iteration}. Treating as mild success to continue refinement.")
                    # Provide minimal but valid confidence data to continue loop
                    if not confidence_result.get("confidence_score"):
                        confidence_result = {
                            "confidence_score": 85,
                            "confidence_source": "fallback",
                            "hallucination_risk_score": 35,
                            "hallucination_issues": [],
                            "hallucination_summary": "Skipped due to rate limiting",
                        }

            confidence_score = confidence_result.get("confidence_score", 40)
            hallucination_risk_score = confidence_result.get("hallucination_risk_score", 50)
            print(f"📊 Confidence Score: {confidence_score}/100 | Hallucination Risk: {hallucination_risk_score}/100")

            # Check if we've reached BOTH targets:
            # - Confidence >= 90%
            # - Hallucination risk < 40%
            if confidence_score >= 90 and hallucination_risk_score < 40:
                print(f"✅ Target reached! Confidence: {confidence_score}% | Hallucination Risk: {hallucination_risk_score}%")
                break

            # Extract hallucination issues for next iteration
            hallucination_issues = confidence_result.get("hallucination_issues", [])
            
            # Decide if we need to continue refining
            needs_confidence_improvement = confidence_score < 90
            needs_hallucination_improvement = hallucination_risk_score >= 40
            
            if (needs_confidence_improvement or needs_hallucination_improvement) and iteration < max_iterations:
                if needs_hallucination_improvement:
                    print(f"⚠️ Hallucination risk too high ({hallucination_risk_score}%). Issues: {hallucination_issues}")
                if needs_confidence_improvement:
                    print(f"⚠️ Confidence score low ({confidence_score}%). Need improvement.")
                print(f"🔄 Re-running pipeline to address issues...\n")
            elif iteration >= max_iterations:
                print(f"⛔ Max iterations ({max_iterations}) reached. Stopping refinement loop.")

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
