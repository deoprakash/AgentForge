from agents.ceo import CEOAgent
from agents.research import ResearchAgent
from agents.writer import WriterAgent
from agents.developer import DeveloperAgent
from agents.automation import AutomationAgent
from utils import format_email_content
import asyncio

class Orchestrator:
    def __init__(self, memory):
        self.ceo = CEOAgent("CEO", memory)
        self.research = ResearchAgent("Research", memory)
        self.writer = WriterAgent("Writer", memory)
        self.developer = DeveloperAgent("Developer", memory)
        self.automation = AutomationAgent("Automation", memory)
        self.memory = memory

    async def run(self, goal, email_target):
    # 🔹 Create session
        session_id = await self.memory.create_session(goal, email_target)

        # 🔹 CEO plan
        plan = await self.ceo.create_plan(goal)
        await self.memory.save_plan(session_id, plan)

        results = []

        # split task by agent
        research_tasks = []
        developer_tasks = []
        writer_tasks = []

        for task in plan.get("tasks", []):
            agent = task.get("assigned_agent")
            desc = task.get("description")

            if agent == "Research":
                # research = await self.research.run_research(desc)
                # await self.memory.save_research(session_id, research)
                research_tasks.append(desc)

            elif agent == "Developer":
                # dev_result = await self.developer.generate_diagram(desc)
                developer_tasks.append(desc)
            
            elif agent == "Writer":
                writer_tasks.append(desc)


        # -----------------------------
        # Parallel execution
        # -----------------------------

        async def run_research():
            output = []
            for desc in research_tasks:
                research = await self.research.run_research(desc)
                await self.memory.save_research(session_id, research)
                output.append(research)
            return output

        async def run_developer():
            output = []
            for desc in developer_tasks:
                dev_result = await self.developer.generate_diagram(desc)
                output.append(dev_result)
            return output
        
        research_results, dev_results = await asyncio.gather(
            run_research(),
            run_developer()
        )

        results.extend(research_results)
        results.extend(dev_results)

        # ----------------------------------
        #  Writer runs After parallel task
        # ----------------------------------

        if writer_tasks:
            # Combine writer tasks with gathered research and dev outputs
            brief = "\n\n".join([
                "\n".join(writer_tasks),
                f"Use this research:\n{research_results}",
                f"Use these outputs:\n{dev_results}"
            ])

            doc = await self.writer.write_document(brief)
            await self.memory.save_document(session_id, doc)
            results.append(doc)



        # Send ONE final email with the completed work
        latest_doc = await self.memory.get_latest_document(session_id)
        if latest_doc:
            email_content = format_email_content(latest_doc.get("document", "Work completed"))
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

        return {
            "session_id": session_id,
            "plan": plan,
            "results": results
        }

