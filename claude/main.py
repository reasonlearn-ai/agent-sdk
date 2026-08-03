import asyncio

from rich.console import Console

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ResultMessage,
    query,
)


async def main():
    console = Console()
    # Agentic loop: streams messages as Claude works
    async for message in query(
        prompt="Run init.",
        options=ClaudeAgentOptions(
            model="claude-sonnet-5",
            allowed_tools=["Read", "Edit", "Glob"],  # Auto-approve these tools
            permission_mode="bypassPermissions",  # Auto-approve file edits
            setting_sources=["project"],
        ),
    ):
        # Print human-readable output
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if hasattr(block, "text"):
                    console.print(block)  # Claude's reasoning
                elif hasattr(block, "name"):
                    console.print(f"Tool: {block}")  # Tool being called
        elif isinstance(message, ResultMessage):
            console.print(f"Done: {message.subtype}")  # Final result


asyncio.run(main())
