import json
import os
from dataclasses import dataclass, asdict

import requests
from openai import OpenAI


@dataclass
class Event:
    id: str
    model: str
    group_id: str
    processing_time: int
    req_tokens: int
    resp_tokens: int
    timestamp: int


def main():
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    request = {
        "model": "gpt-4o",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Please say something nice."},
        ],
    }

    res = client.chat.completions.with_raw_response.create(**request)
    headers = dict(res.headers)
    result = res.parse().model_dump()

    event = asdict(Event(
        id=result["id"],
        model=request["model"],
        group_id="group01",
        processing_time=int(headers["openai-processing-ms"]),
        req_tokens=result["usage"]["prompt_tokens"],
        resp_tokens=result["usage"]["completion_tokens"],
        timestamp=result["created"],
    ))
    print(json.dumps(event, indent=4))

    res = requests.post(
        "https://api.airfold.co/v1/events/events",
        json=event,
        headers={"Authorization": f"Bearer {os.environ['AIRFOLD_API_KEY']}"},
    )
    if not res.ok:
        print(res)


if __name__ == "__main__":
    main()
