import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions, ResultMessage

session_id = "..."  # The ID you captured in the previous example


async def main():
    # Fork: branch from session_id into a new session
    forked_id = None
    try:
        async for message in query(
            prompt="Instead of JWT, outline how OAuth2 would work for the auth module",
            options=ClaudeAgentOptions(
                resume=session_id,
                fork_session=True,
                max_turns=5,
            ),
        ):
            if isinstance(message, ResultMessage):
                forked_id = (
                    message.session_id
                )  # The fork's ID, distinct from session_id
                if message.subtype == "success":
                    print(message.result)
    except Exception as error:
        # A single-shot query() raises after yielding an error result. If the
        # failure was an error result, forked_id was already captured by the
        # loop above; connection or process failures yield no result message.
        print(f"Session ended with an error: {error}")

    print(f"Forked session: {forked_id}")

    # Original session is untouched; resuming it continues the JWT thread
    try:
        async for message in query(
            prompt="Continue with the JWT approach",
            options=ClaudeAgentOptions(resume=session_id),
        ):
            if isinstance(message, ResultMessage) and message.subtype == "success":
                print(message.result)
    except Exception as error:
        # A single-shot query() raises after yielding an error result.
        print(f"Session ended with an error: {error}")


asyncio.run(main())
