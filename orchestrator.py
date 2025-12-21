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
from agents.reviewer import ReviewerAgent
from agents.confidence import ConfidenceAgent
from utils import format_email_content


class Orchestrator:
    def __init__(self, memory):
        self.ceo = CEOAgent("CEO", memory)
        self.research = ResearchAgent("Research", memory)
        self.writer = WriterAgent("Writer", memory)
        self.developer = DeveloperAgent("Developer", memory)
        self.automation = AutomationAgent("Automation", memory)
        self.reviewer = ReviewerAgent("Reviewer", memory)
        self.confidence = ConfidenceAgent("Confidence", memory)
        self.memory = memory

    async def run(self, goal, email_target):
        # -----------------------------
        # 1️⃣ Create session
        # -----------------------------
        session_id = await self.memory.create_session(goal, email_target)

        # -----------------------------
        # 2️⃣ CEO creates plan
        # -----------------------------
        plan = await self.ceo.create_plan(goal)
        await self.memory.save_plan(session_id, plan)

        results = []

        # -----------------------------
        # 3️⃣ Research + Developer (SEQUENTIAL)
        # -----------------------------
        research_results = []
        developer_results = []

        for task in plan.get("tasks", []):
            agent = task.get("assigned_agent")
            desc = task.get("description")

            if agent == "Research":
                research = await self.research.run_research(desc)
                await self.memory.save_research(session_id, research)
                research_results.append(research)
                results.append(research)

            elif agent == "Developer":
                dev_result = await self.developer.generate_diagram(desc)
                developer_results.append(dev_result)
                results.append(dev_result)

        # -----------------------------
        # 4️⃣ Writer + Reviewer + Confidence
        # -----------------------------
        writer_task = next(
            (t["description"] for t in plan.get("tasks", [])
             if t["assigned_agent"] == "Writer"),
            None
        )

        confidence_report = None  # IMPORTANT

        if writer_task:
            brief = f"""
            {writer_task}

            Use this research:
            {research_results}

            Use these diagrams / outputs:
            {developer_results}
            """

            doc = await self.writer.write_document(brief)

            # ==================================================
            # 🧠 HITL: LLM quota exhausted
            # ==================================================
            if "__LLM_UNAVAILABLE__" in doc.get("document", ""):
                await self.memory.save_actions(session_id, {
                    "type": "human_in_loop",
                    "status": "PENDING",
                    "reason": "LLM quota exhausted",
                    "allowed_actions": ["retry_now", "retry_later", "cancel"]
                })

                return {
                    "session_id": session_id,
                    "plan": plan,
                    "status": "WAITING_FOR_HUMAN",
                    "message": "LLM quota exhausted. Human approval required."
                }

            await self.memory.save_document(session_id, doc)

            # -----------------------------
            # 🔍 Reviewer
            # -----------------------------
            review = await self.reviewer.review(doc["document"])

            if review["status"] == "REVISE":
                improved_brief = f"""
                Improve the document using this feedback:

                Feedback:
                {review["feedback"]}

                Original Document:
                {doc["document"]}
                """
                doc = await self.writer.write_document(improved_brief)
                await self.memory.save_document(session_id, doc)

            # -----------------------------
            # 🧠 Confidence + Hallucination
            # -----------------------------
            confidence_report = await self.confidence.evaluate(doc["document"])

            await self.memory.save_actions(session_id, {
                "type": "confidence_report",
                "data": confidence_report
            })

            # ==================================================
            # 🚨 HITL if confidence parsing failed
            # ==================================================
            if "Failed to parse" in str(confidence_report.get("issues", [])):
                await self.memory.save_actions(session_id, {
                    "type": "human_in_loop",
                    "status": "PENDING",
                    "reason": "Confidence evaluation parsing failed",
                    "allowed_actions": ["approve_send", "request_revision", "cancel"]
                })

                return {
                    "session_id": session_id,
                    "plan": plan,
                    "status": "WAITING_FOR_HUMAN",
                    "message": "Confidence evaluation failed. Human review required."
                }

            # 🔁 Auto-revise if hallucination risk is HIGH
            if confidence_report["verdict"] == "REVISE":
                safety_brief = f"""
                Reduce hallucinations and unsupported claims.
                Use only verified research below.

                Issues:
                {confidence_report["issues"]}

                Research:
                {research_results}

                Document:
                {doc["document"]}
                """
                doc = await self.writer.write_document(safety_brief)
                await self.memory.save_document(session_id, doc)

            # ✍️ Auto-soften if WARNING
            elif confidence_report["verdict"] == "WARNING":
                refine_brief = f"""
                Revise the document to:
                - Use cautious, professional language
                - Avoid absolute or overconfident claims
                - Clearly indicate assumptions
                - Improve clarity

                Issues:
                {confidence_report["issues"]}

                Document:
                {doc["document"]}
                """
                doc = await self.writer.write_document(refine_brief)
                await self.memory.save_document(session_id, doc)

            results.append({
                "document": doc,
                "confidence": confidence_report
            })

        # -----------------------------
        # 5️⃣ Send final email (STRICT SAFE)
        # -----------------------------
        latest_doc = await self.memory.get_latest_document(session_id)

        if latest_doc and confidence_report:
            content = latest_doc.get("document", "")

            if confidence_report["verdict"] == "REVISE":
                await self.memory.save_actions(session_id, {
                    "type": "email_blocked",
                    "reason": "Confidence verdict = REVISE"
                })
                print("🚫 Email blocked due to high hallucination risk")

            elif "__LLM_UNAVAILABLE__" not in content:
                email_content = format_email_content(content)
                sent = await self.automation.send_output(
                    email_target,
                    f"Final Draft: {plan.get('goal', 'Your Request')}",
                    email_content
                )
                await self.memory.save_actions(session_id, sent)
                results.append({
                    "email_sent": True,
                    "formatted_output": email_content,
                    "details": sent
                })

        # -----------------------------
        # 6️⃣ Final response
        # -----------------------------
        return {
            "session_id": session_id,
            "plan": plan,
            "results": results
        }

    async def resume(self, session_id: str):
        """Resume a paused session (e.g., after LLM quota exhaustion).

        Strategy:
        - Load latest plan for the session
        - Load saved research; regenerate developer outputs as needed
        - Continue Writer → Reviewer → Confidence → Email
        """

        plan = await self.memory.get_latest_plan(session_id)
        if not plan:
            return {
                "session_id": session_id,
                "status": "ERROR",
                "message": "No plan found for session. Cannot resume."
            }

        # Gather previously saved research
        research_results = await self.memory.get_research(session_id)

        # Re-run developer tasks (not persisted previously)
        developer_results = []
        for task in plan.get("tasks", []):
            if task.get("assigned_agent") == "Developer":
                desc = task.get("description")
                dev_result = await self.developer.generate_diagram(desc)
                developer_results.append(dev_result)

        # Find writer task or create a default brief
        writer_task = next(
            (t["description"] for t in plan.get("tasks", [])
             if t.get("assigned_agent") == "Writer"),
            None
        )

        brief = f"""
        {writer_task or 'Compose the final document/draft using the research and diagrams.'}

        Use this research:
        {research_results}

        Use these diagrams / outputs:
        {developer_results}
        """

        # Continue with Writer
        doc = await self.writer.write_document(brief)
        if "__LLM_UNAVAILABLE__" in doc.get("document", ""):
            return {
                "session_id": session_id,
                "status": "PENDING_LLM_QUOTA",
                "message": "LLM quota exhausted. Retry later."
            }

        await self.memory.save_document(session_id, doc)

        # Reviewer
        review = await self.reviewer.review(doc["document"])
        if review["status"] == "REVISE":
            improved_brief = f"""
            Improve the document using this feedback:

            Feedback:
            {review["feedback"]}

            Original Document:
            {doc["document"]}
            """
            doc = await self.writer.write_document(improved_brief)
            await self.memory.save_document(session_id, doc)

        # Confidence
        confidence_report = await self.confidence.evaluate(doc["document"])
        await self.memory.save_actions(session_id, {
            "type": "confidence_report",
            "data": confidence_report
        })

        if confidence_report.get("verdict") == "REVISE":
            safety_brief = f"""
            Reduce hallucinations and unsupported claims.
            Use only verified research below.

            Issues:
            {confidence_report.get("issues")}

            Research:
            {research_results}

            Document:
            {doc["document"]}
            """
            doc = await self.writer.write_document(safety_brief)
            await self.memory.save_document(session_id, doc)

        # Fetch latest document; the /approve flow does not provide an email,
        # so we return results without sending.
        latest_doc = await self.memory.get_latest_document(session_id)

        return {
            "session_id": session_id,
            "plan": plan,
            "results": {
                "research": research_results,
                "developer": developer_results,
                "document": latest_doc,
                "confidence": confidence_report
            }
        }
