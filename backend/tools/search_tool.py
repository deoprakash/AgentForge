class SearchTool:
    async def search(self, query):
        print(f"[SEARCH] {query}")
        return [f"Result for {query} #{i}" for i in range(1, 4)]