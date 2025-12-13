from agents.base import BaseAgent
from tools.gmail_tool import GmailTool

gmail = GmailTool()

class AutomationAgent(BaseAgent):
    async def send_output(self, email, subject, content):
        return await gmail.send(email, subject, content)