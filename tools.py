from crewai_tools import JSONSearchTool
# search_tool = search
        
json_tool = JSONSearchTool(
    csv='out.json',
    config=dict(
        llm=dict(
            provider="ollama",
            config=dict(
                model="gemma3:12b",
            ),
        ),
        embedder=dict(
            provider="huggingface",
            config=dict(
                model="sentence-transformers/all-MiniLM-L6-v2",
            ),
        ),
    )
)


