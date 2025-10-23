# MCP Sampling Capability Research

## Overview

This document provides research findings on the MCP (Model Context Protocol) client capability "sampling" as defined in the MCP specification version 2025-06-18.

## What is MCP Sampling?

MCP Sampling is a capability that allows MCP servers to request language model completions from the client. This enables servers to leverage AI capabilities while maintaining user control and security through a "human-in-the-loop" process.

## Key Concepts

### 1. Capability Declaration

During the initialization handshake, clients declare their capabilities including whether they support sampling:

```json
{
  "capabilities": {
    "sampling": {}
  }
}
```

The server must check for this capability before attempting to use sampling features.

### 2. Sampling Request Flow

The typical flow for using sampling is:

1. **Server checks client capability**: Before making a sampling request, the server verifies that the client supports the `sampling` capability
2. **Server creates request**: The server constructs a `sampling/createMessage` request with:
   - Messages (conversation history)
   - Model preferences (optional hints about which model to use)
   - System prompt (optional)
   - Max tokens
   - Other parameters (temperature, stop sequences, etc.)
3. **Client validates**: The client receives the request and may present it to the user for approval or modification
4. **LLM generation**: Once approved, the client sends the prompt to the configured language model
5. **User review**: The client may allow the user to review and modify the generated response
6. **Response returned**: The client returns the approved response to the server

### 3. Request Structure

A sampling request follows this structure:

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "sampling/createMessage",
  "params": {
    "messages": [
      {
        "role": "user",
        "content": {
          "type": "text",
          "text": "What is the capital of France?"
        }
      }
    ],
    "modelPreferences": {
      "hints": [
        { "name": "claude-3-sonnet" }
      ],
      "intelligencePriority": 0.8,
      "speedPriority": 0.5
    },
    "systemPrompt": "You are a helpful assistant.",
    "maxTokens": 100
  }
}
```

### 4. Response Structure

The client returns a response with the generated content:

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "role": "assistant",
    "content": {
      "type": "text",
      "text": "The capital of France is Paris."
    },
    "model": "claude-3-sonnet-20240307",
    "stopReason": "endTurn"
  }
}
```

## Python Implementation with MCP SDK

### Checking Client Capabilities

```python
from mcp.server.session import ServerSession
from mcp import types

# In a tool or request handler where you have access to the session
session: ServerSession = context.session

# Check if client supports sampling
has_sampling = session.check_client_capability(types.ClientCapabilities.sampling)

if not has_sampling:
    return "Error: Client does not support sampling capability"
```

### Creating a Sampling Request

```python
from mcp import types

# Create messages for the conversation
messages = [
    types.SamplingMessage(
        role="user",
        content=types.TextContent(
            type="text",
            text="What is the capital of France?"
        )
    )
]

# Make the sampling request
result = await session.create_message(
    messages=messages,
    max_tokens=100,
    system_prompt="You are a helpful assistant.",
    temperature=0.7,
    model_preferences=types.ModelPreferences(
        hints=[types.ModelHint(name="claude-3-sonnet")],
        intelligencePriority=0.8,
        speedPriority=0.5
    )
)

# Access the response
response_text = result.content.text
model_used = result.model
stop_reason = result.stopReason
```

## Security and Privacy Considerations

### Human-in-the-Loop

The sampling mechanism is designed with security in mind:

1. **User Approval**: Clients can require user approval before sending requests to the LLM
2. **Request Review**: Users can inspect and modify the prompts before they are sent
3. **Response Review**: Users can review and edit the generated responses before they are returned to the server
4. **Context Control**: Servers can specify what context to include (`none`, `thisServer`, `allServers`)

### Best Practices

1. **Always check capability**: Never assume the client supports sampling
2. **Provide clear prompts**: Make it obvious to the user what the server is requesting
3. **Limit token usage**: Set appropriate `maxTokens` to prevent excessive resource usage
4. **Handle errors gracefully**: Sampling requests can fail or be rejected by users
5. **Respect privacy**: Be careful about what information you include in sampling requests

## Use Cases

### 1. Content Generation

Servers can use sampling to generate content based on data they have access to:
- Summarizing API responses
- Generating natural language descriptions of data
- Creating documentation or explanations

### 2. Data Analysis

Servers can ask the LLM to analyze or interpret data:
- Analyzing code patterns
- Interpreting API responses
- Providing insights on data trends

### 3. Interactive Assistance

Servers can create more interactive experiences:
- Asking clarifying questions
- Providing contextual help
- Generating examples or suggestions

### 4. Multi-Step Reasoning

Servers can use sampling in combination with tools:
- Use a tool to fetch data
- Use sampling to analyze or interpret the data
- Return enhanced results to the user

## Implementation Example

Here's a complete example of a tool that uses sampling:

```python
@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """Execute a tool with given arguments."""
    if name == "analyze_github_user":
        # Get session from context (implementation-specific)
        session = get_current_session()
        
        # Check if client supports sampling
        if not session.check_client_capability(types.ClientCapabilities.sampling):
            return [TextContent(
                type="text",
                text="Error: This tool requires sampling capability, but the client does not support it."
            )]
        
        # Fetch user data
        username = arguments.get("username", "octocat")
        user_data = await fetch_github_user(username)
        
        # Create a sampling request to analyze the data
        messages = [
            types.SamplingMessage(
                role="user",
                content=types.TextContent(
                    type="text",
                    text=f"Analyze this GitHub user data and provide insights: {json.dumps(user_data)}"
                )
            )
        ]
        
        result = await session.create_message(
            messages=messages,
            max_tokens=500,
            system_prompt="You are a GitHub data analyst. Provide concise, actionable insights.",
            temperature=0.7
        )
        
        return [TextContent(
            type="text",
            text=f"Analysis:\n\n{result.content.text}"
        )]
```

## References

- [MCP Specification - Sampling](https://modelcontextprotocol.io/specification/2025-06-18/client/sampling)
- [MCP Specification - Lifecycle](https://modelcontextprotocol.io/specification/2025-06-18/basic/lifecycle)
- [Understanding MCP Sampling - Enabling Servers to Access LLMs](https://mingzilla.github.io/specification/mcp-sampling-guide.html)
- [MCP Sampling Explained: Adding Intelligence to Your MCP Servers](https://www.mcpevals.io/blog/mcp-sampling-explained)
- [MCP for Beginners - Sampling](https://github.com/microsoft/mcp-for-beginners/blob/main/05-AdvancedTopics/mcp-sampling/README.md)

## Conclusion

MCP Sampling is a powerful capability that enables servers to leverage language models while maintaining user control and security. By following the best practices outlined in this document, developers can create more intelligent and interactive MCP servers that provide enhanced value to users.

The key takeaways are:
1. Always check for client capability support before using sampling
2. Design prompts that are clear and purposeful
3. Implement proper error handling for sampling requests
4. Respect user privacy and control throughout the process
5. Use sampling to enhance, not replace, the server's core functionality
