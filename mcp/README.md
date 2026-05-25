# MCP Module

This module contains code examples showcasing MCP and it's various implementations.

1. `weather/` : A simple weather MCP server that has few tools and prompts. Follow the below steps to spin up the MCP server and interact with it, You would need claude desktop for it.
    * Add this config in claude_desktop_config.json in "mcpServers" section to enable the MCP server in Claude Desktop
        ```json
            "local_weather": {
            "command": "uv",
            "args": [
                "--directory",
                "/<path_to_project>/mcp/weather",
                "run",
                "weather.py"
                ]
            }   
        ```
    * Use this follwoing prompt to test the tool in Claude Desktop
        1. What’s the weather forecast in Texas ? Use the local_weather tool. Use TX as code for Texas.  and also provide its lattitude and longitude
        2. What’s the weather in Texas ? Use the local_weather tool. Use TX as code for Texas.
        3. Access the prompt from Connectors section and add to US cities to use the prompt.  

