import asyncio

from rich.console import Console

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ResultMessage,
    query,
)

options = (
    ClaudeAgentOptions(
        model="claude-sonnet-4-5",
        allowed_tools=["Read", "Edit", "Glob", "Write"],  # Auto-approve these tools
        permission_mode="bypassPermissions",  # Auto-approve file edits
        setting_sources=["project"],
        skills=["all"],
    ),
)


async def promptClaude(prompt: str, options: ClaudeAgentOptions):
    console = Console()
    # Agentic loop: streams messages as Claude works
    async for message in query(
        prompt=prompt,
        options=options,
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


if __name__ == "__main__":
    asyncio.run(
        promptClaude(
            "What skills do you have?",
            ClaudeAgentOptions(),
        )
    )

    asyncio.run(
        promptClaude(
            "Review utils.py for bugs that would cause crashes. Fix any issues you find and summarize changes made.",
            ClaudeAgentOptions(),
        )
    )
