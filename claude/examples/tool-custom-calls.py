import json
import httpx
import asyncio
from typing import Any
from pydantic import BaseModel
from claude_agent_sdk import (
    ClaudeAgentOptions,
    tool,
    create_sdk_mcp_server,
    query,
    ResultMessage,
    AssistantMessage,
    ToolUseBlock,
    InMemorySessionStore,
)


class ResponseText(BaseModel):
    results: str
    steps: list[str]


@tool(
    "fetch_data",
    "Fetch data from an API",
    {"endpoint": str},  # Simple schema
)
async def fetch_data(args: dict[str, Any]) -> dict[str, Any]:
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(args["endpoint"])
            if response.status_code != 200:
                # Return the failure as a tool result so Claude can react to it.
                # is_error marks this as a failed call rather than odd-looking data.
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": f"API error: {response.status_code} {response.reason_phrase}",
                        }
                    ],
                    "is_error": True,
                }

            data = response.json()
            return {"content": [{"type": "text", "text": json.dumps(data, indent=2)}]}
    except Exception as e:
        # Composes the message Claude reads. An uncaught exception would
        # reach Claude as the raw str(e) with no context.
        return {
            "content": [{"type": "text", "text": f"Failed to fetch data: {str(e)}"}],
            "is_error": True,
        }


@tool(
    "get_precipitation_chance",
    "Get the hourly precipitation probability for a location. "
    "Optionally pass 'hours' (1-24) to control how many hours to return.",
    {"latitude": float, "longitude": float},
)
async def get_precipitation_chance(args: dict[str, Any]) -> dict[str, Any]:
    # 'hours' isn't in the schema - read it with .get() to make it optional
    hours = args.get("hours", 12)
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": args["latitude"],
                "longitude": args["longitude"],
                "hourly": "precipitation_probability",
                "forecast_days": 1,
            },
        )
        data = response.json()
    chances = data["hourly"]["precipitation_probability"][:hours]

    return {
        "content": [
            {
                "type": "text",
                "text": f"Next {hours} hours: {'%, '.join(map(str, chances))}%",
            }
        ]
    }


# z.enum() in TypeScript becomes an "enum" constraint in JSON Schema.
# The dict schema has no equivalent, so full JSON Schema is required.
@tool(
    "convert_units",
    "Convert a value from one unit to another",
    {
        "type": "object",
        "properties": {
            "unit_type": {
                "type": "string",
                "enum": ["length", "temperature", "weight"],
                "description": "Category of unit",
            },
            "from_unit": {
                "type": "string",
                "description": "Unit to convert from, e.g. kilometers, fahrenheit, pounds",
            },
            "to_unit": {"type": "string", "description": "Unit to convert to"},
            "value": {"type": "number", "description": "Value to convert"},
        },
        "required": ["unit_type", "from_unit", "to_unit", "value"],
    },
)
async def convert_units(args: dict[str, Any]) -> dict[str, Any]:
    conversions = {
        "length": {
            "kilometers_to_miles": lambda v: v * 0.621371,
            "miles_to_kilometers": lambda v: v * 1.60934,
            "meters_to_feet": lambda v: v * 3.28084,
            "feet_to_meters": lambda v: v * 0.3048,
        },
        "temperature": {
            "celsius_to_fahrenheit": lambda v: (v * 9) / 5 + 32,
            "fahrenheit_to_celsius": lambda v: (v - 32) * 5 / 9,
            "celsius_to_kelvin": lambda v: v + 273.15,
            "kelvin_to_celsius": lambda v: v - 273.15,
        },
        "weight": {
            "kilograms_to_pounds": lambda v: v * 2.20462,
            "pounds_to_kilograms": lambda v: v * 0.453592,
            "grams_to_ounces": lambda v: v * 0.035274,
            "ounces_to_grams": lambda v: v * 28.3495,
        },
    }

    key = f"{args['from_unit']}_to_{args['to_unit']}"
    fn = conversions.get(args["unit_type"], {}).get(key)

    if not fn:
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"Unsupported conversion: {args['from_unit']} to {args['to_unit']}",
                }
            ],
            "is_error": True,
        }

    result = fn(args["value"])
    return {
        "content": [
            {
                "type": "text",
                "text": f"{args['value']} {args['from_unit']} = {result:.4f} {args['to_unit']}",
            }
        ]
    }


# wrap the tool in an in-process mcp server
weather_server = create_sdk_mcp_server(
    name="server_of_tools",
    version="1.0.0",
    tools=[fetch_data, get_precipitation_chance, convert_units],
)

store = InMemorySessionStore()

options = ClaudeAgentOptions(
    mcp_servers={"server_of_tools": weather_server},
    allowed_tools=["mcp__server_of_tools__*", "Read", "Edit", "Glob", "Write"],
    model="claude-sonnet-4-5",
    permission_mode="bypassPermissions",  # Auto-approve file edits
    setting_sources=["project"],
    skills=["all"],
    session_store=store,
    output_format={
        "type": "json_schema",
        "schema": ResponseText.model_json_schema(),
    },
)


async def main():
    prompts = [
        "Remember that my name is Charlie",
        "What's the temperature and chance of precipitation in San Francisco?",
        "Convert 100 kilometers to miles.",
        "What is 72°F in Celsius?",
        "How many pounds is 5 kilograms?",
        "What's the temperature and chance of precipitation in San Francisco?",
        "What is my name?",
    ]

    session_id = None

    for prompt in prompts:
        options = ClaudeAgentOptions(
            system_prompt="You are a helpful assistant that can call tools to fetch data, get weather information, and convert units. Do not use any tools that are not explicitly allowed. If you encounter an error when calling a tool, please handle it gracefully and inform the user. Do repeat tool calls unnecessarily. If you are unsure about the input, ask for clarification instead of making assumptions. If you have prior context from previous interactions, use it to inform your responses.",
            mcp_servers={"server_of_tools": weather_server},
            allowed_tools=["mcp__server_of_tools__*", "Read", "Edit", "Glob", "Write"],
            model="claude-sonnet-4-5",
            permission_mode="bypassPermissions",  # Auto-approve file edits
            setting_sources=["project"],
            skills=["all"],
            session_store=store,
            output_format={
                "type": "json_schema",
                "schema": ResponseText.model_json_schema(),
            },
            resume=session_id if session_id is not None else None,
        )
        try:
            async for message in query(
                prompt=prompt,
                options=options,
            ):
                if isinstance(message, AssistantMessage):
                    for block in message.content:
                        if isinstance(block, ToolUseBlock):
                            print(f"[tool call] {block.name}({block.input})")
                if isinstance(message, ResultMessage) and message.structured_output:
                    # Validate and get fully typed result
                    session_id = (
                        message.session_id if session_id is None else session_id
                    )
                    response = ResponseText.model_validate(message.structured_output)
                    print(f"Session ID: {message.session_id}")
                    print(f"Results: {response.results}")
                    print(f"Steps: {response.steps}")
                    cost = (
                        f"${message.total_cost_usd:.4f}"
                        if message.total_cost_usd is not None
                        else "N/A"
                    )
                    print(f"[done: {message.subtype}, cost: {cost}]")
                    print("-" * 40)
        except Exception as error:
            # A single-shot query() raises after yielding an error result. Only success
            # results are printed above, so handle the failure here and continue with
            # the next prompt.
            print(f"Call failed: {error}")


if __name__ == "__main__":
    asyncio.run(main())
