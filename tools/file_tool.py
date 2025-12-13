import os

class FileTool:
    async def save(self, filename, content):
        os.makedirs("outputs", exist_ok=True)
        path = f"outputs/{filename}"
        with open(path, "wb") as f:
            f.write(content)
        return path