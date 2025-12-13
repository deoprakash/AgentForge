from agents.ceo import CEOAgent
from agents.research import ResearchAgent
from agents.writer import WriterAgent
from agents.developer import DeveloperAgent
from agents.automation import AutomationAgent

class Orchestrator:
    def __init__(self, memory):
        self.ceo = CEOAgent("CEO", memory)
        self.research = ResearchAgent("Research", memory)
        self.writer = WriterAgent("Writer", memory)
        self.developer = DeveloperAgent("Developer", memory)
        self.automation = AutomationAgent("Automation", memory)
        self.memory = memory

    async def run(self, goal, email_target):
        plan = await self.ceo.create_plan(goal)
        results = []

        for task in plan.get("tasks", []):
            agent = task.get("assigned_agent")
            desc = task.get("description")

            if agent == "Research":
                results.append(await self.research.run_research(desc))
            
            elif agent == "Writer":
                results.append(await self.writer.write_document(desc))

            elif agent == "Developer":
                results.append(await self.developer.generate_diagram(desc))

            elif agent == "Automation":
                results.append(await self.automation.send_output(email_target, "Task Done", desc))
        
        return {"plan": plan, "results": results}
