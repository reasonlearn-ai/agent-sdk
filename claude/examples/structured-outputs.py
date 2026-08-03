import asyncio
from pydantic import BaseModel
from claude_agent_sdk import query, ClaudeAgentOptions, ResultMessage


class Step(BaseModel):
    step_number: int
    description: str
    estimated_complexity: str  # 'low', 'medium', 'high'


class FeaturePlan(BaseModel):
    feature_name: str
    summary: str
    steps: list[Step]
    risks: list[str]


async def main():
    try:
        async for message in query(
            prompt="Plan 2 steps to read and fix bugs in a codebase.",
            options=ClaudeAgentOptions(
                output_format={
                    "type": "json_schema",
                    "schema": FeaturePlan.model_json_schema(),
                }
            ),
        ):
            if isinstance(message, ResultMessage) and message.structured_output:
                # Validate and get fully typed result
                plan = FeaturePlan.model_validate(message.structured_output)
                print(f"Feature: {plan.feature_name}")
                print(f"Summary: {plan.summary}")
                for step in plan.steps:
                    print(
                        f"{step.step_number}. [{step.estimated_complexity}] {step.description}"
                    )
    except Exception as error:
        # A single-shot query() raises after yielding an error result, such as
        # error_max_structured_output_retries; see the Error handling section.
        print(f"Session ended with an error: {error}")


asyncio.run(main())
