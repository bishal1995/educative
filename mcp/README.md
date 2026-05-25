# MCP Module

This module contains code examples showcasing MCP and it's various implementations.

1. `weather/` : A simple bare shell weather MCP server that has few tools and prompts. Follow the below steps to spin up the MCP server and interact with it, You would need claude desktop for it.
    * Add this config in claude_desktop_config.json in "mcpServers" section to enable the MCP server in Claude Desktop
        ```json
            "local_weather": {
            "command": "uv",
            "args": [
                "--directory",
                "/<path_to_project_with_pyptoject_toml_file>/",
                "run",
                "<directory_sub_location_wrt_pyproject_toml_file>/weather.py"
                ]
            }   
        ```
    * Use this following prompt to test the tool in Claude Desktop.
        1. What’s the weather forecast in Texas ? Use the local_weather tool. Use TX as code for Texas.  and also provide its lattitude and longitude
        2. What’s the weather in Texas ? Use the local_weather tool. Use TX as code for Texas.
        3. Access the prompt from Connectors section and add to US cities to use the prompt.  

2. `rag_mcp/` : A mcp implemetation with RAG using chromaDB
    * Add this config in claude_desktop_config.json in "mcpServers" section to enable the MCP server in Claude Desktop
        ```json
            "employee_handbook": {
                "command": "uv",
                "args": [
                "--directory",
                "/Users/bishal/work/educative/become_a_llm_engineer/",
                "run",
                "mcp/rag_mcp/employee_mcp.py"
                ]
            }     
        ```

    * Use this prompts to use the tool
        1. You are a helpful RAG assistant using employee_handbook mcp server. Your role is to answer questions using the content of documents provided by the user. Use the ingestion tool to load the employee handbook, answer this qustion : `paste Your question here` 
        by using the query tool to find the relevant context within the ingested documents and use that context to form a clear answer.