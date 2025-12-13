from agents.ceo import CEOAgent
from agents.research import ResearchAgent
from agents.writer import WriterAgent
from agents.developer import DeveloperAgent
from agents.automation import AutomationAgent
from utils import format_email_content

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

        for task in plan.get("tasks", []):
            agent = task.get("assigned_agent")
            desc = task.get("description")

            if agent == "Research":
                research = await self.research.run_research(desc)
                await self.memory.save_research(session_id, research)
                results.append(research)

            elif agent == "Writer":
                past_research = await self.memory.get_research(session_id)
                brief = f"{desc}\n\nUse this research:\n{past_research}"
                doc = await self.writer.write_document(brief)
                await self.memory.save_document(session_id, doc)
                results.append(doc)

            elif agent == "Developer":
                dev_result = await self.developer.generate_diagram(desc)
                results.append(dev_result)

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

