import asyncio
from claude_agent_sdk import (
    ClaudeSDKClient,
    ClaudeAgentOptions,
    AssistantMessage,
    ResultMessage,
    TextBlock,
)


def print_response(message):
    """Print only the human-readable parts of a message."""
    if isinstance(message, AssistantMessage):
        for block in message.content:
            if isinstance(block, TextBlock):
                print(block.text)
    elif isinstance(message, ResultMessage):
        cost = (
            f"${message.total_cost_usd:.4f}"
            if message.total_cost_usd is not None
            else "N/A"
        )
        print(f"[done: {message.subtype}, cost: {cost}]")


async def main():
    options = ClaudeAgentOptions(
        allowed_tools=["Read", "Edit", "Glob", "Grep"],
    )

    async with ClaudeSDKClient(options=options) as client:
        # First query: client captures the session ID internally
        await client.query("Analyze the auth module")
        async for message in client.receive_response():
            print_response(message)

        # Second query: automatically continues the same session
        await client.query("Now refactor it to use JWT")
        async for message in client.receive_response():
            print_response(message)


if __name__ == "__main__":
    asyncio.run(main())

    """
    import asyncio
    from claude_agent_sdk import query, ClaudeAgentOptions, ResultMessage

    session_id = "..."  # The ID you captured in the previous example


    async def main():
        # Earlier session analyzed the code; now build on that analysis
        async for message in query(
            prompt="Now implement the refactoring you suggested",
            options=ClaudeAgentOptions(
                resume=session_id,
                allowed_tools=["Read", "Edit", "Write", "Glob", "Grep"],
            ),
        ):
            if isinstance(message, ResultMessage) and message.subtype == "success":
                print(message.result)


    asyncio.run(main())
    """
