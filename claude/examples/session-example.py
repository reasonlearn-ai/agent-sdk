import asyncio
from claude_agent_sdk import (
    ClaudeAgentOptions,
    InMemorySessionStore,
    ResultMessage,
    query,
)

store = InMemorySessionStore()


async def main():
    session_id = None
    try:
        async for message in query(
            prompt="List the MD files under docs/",
            options=ClaudeAgentOptions(session_store=store),
        ):
            if isinstance(message, ResultMessage):
                session_id = message.session_id
                print(session_id)
    except Exception as error:
        # A single-shot query() raises after yielding an error result. If the
        # failure was an error result, session_id was already captured by the
        # loop above; connection or process failures yield no result message.
        print(f"Session ended with an error: {error}")

    # Resume from the store. The agent has full context from the first call.
    async for message in query(
        prompt="Summarize what those files do",
        options=ClaudeAgentOptions(session_store=store, resume=session_id),
    ):
        if isinstance(message, ResultMessage) and message.subtype == "success":
            print(message.result)


if __name__ == "__main__":
    asyncio.run(main())
