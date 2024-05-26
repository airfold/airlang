import json
import logging
import os
from dataclasses import asdict, dataclass
from typing import Dict, List

import requests
import typer
from openai import OpenAI
from rich.console import Console
from rich.logging import RichHandler

# Initialize Rich logging
console = Console()
logging.basicConfig(level="INFO", handlers=[RichHandler(console=console)])
logger = logging.getLogger("rich")


@dataclass
class Event:
    id: str
    model: str
    group_id: str
    processing_time: int
    req_tokens: int
    resp_tokens: int
    timestamp: int


def process_request(client: OpenAI, model: str, messages: List[Dict[str, str]], group_id: str) -> Event:
    request = {
        "model": model,
        "messages": messages,
    }

    logger.info("Sending request to OpenAI API...")
    res = client.chat.completions.with_raw_response.create(**request)
    headers = dict(res.headers)
    result = res.parse().model_dump()

    event = asdict(
        Event(
            id=result["id"],
            model=request["model"],
            group_id=group_id,
            processing_time=int(headers.get("openai-processing-ms", 0)),
            req_tokens=result["usage"]["prompt_tokens"],
            resp_tokens=result["usage"]["completion_tokens"],
            timestamp=result["created"],
        )
    )

    logger.info("Request processed successfully.")
    logger.debug(f"Event: {json.dumps(event, indent=4)}")

    return event


def send_event(event: Event, api_url: str, api_key: str):
    logger.info("Sending event to Airfold API...")
    res = requests.post(
        api_url,
        json=event,
        headers={"Authorization": f"Bearer {api_key}"},
    )
    if not res.ok:
        logger.error(f"Failed to send event: {res.text}")
    else:
        logger.info("Event sent successfully.")


def main(
    num_requests: int = typer.Option(100, help="Number of requests to process."),
    model: str = typer.Option("gpt-4o", help="Model to use for the requests."),
    group_id: str = typer.Option("group01", help="Group ID for the events."),
    api_url: str = typer.Option("https://api.airfold.co/v1/events/events", help="API URL to send events."),
    openai_api_key: str = typer.Option(..., envvar="OPENAI_API_KEY", help="OpenAI API key."),
    airfold_api_key: str = typer.Option(..., envvar="AIRFOLD_API_KEY", help="Airfold API key."),
):
    client = OpenAI(api_key=openai_api_key)
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Please say something nice."},
    ]

    for i in range(num_requests):
        logger.info(f"Processing request {i + 1} of {num_requests}...")
        event = process_request(client, model, messages, group_id)
        send_event(event, api_url, airfold_api_key)
        logger.info(f"Completed request {i + 1} of {num_requests}.")


if __name__ == "__main__":
    typer.run(main)
