## Airlang: simple flexible LLM monitoring with Airfold

### Install

Install the project into venv:

```shell
python3 -m venv .venv
. ./.venv/bin/activate
pip install -e .
```

### Configure

Before we begin, we need to create a workspace to store our data and resources, as well as a token to authenticate our CLI.

Go to [Airfold](https://app.airfold.co/) and create a new workspace.  
Copy an Admin token from the workspace’s Token page.  
The token should look like this: `aft_6eab8fcd902e4cbfb63ba174469989cd.Ds1PME5dQsJKosKQWVcZiBSlRFBbmhzIocvHg8KQddV`.

Then you can configure airfold CLI, by running `af config`:

```shell
$ af config
Configuring for API URL: https://api.airfold.co
? Api key: aft_6eab8fcd902e4cbfb63ba174469989cd.Ds1PME5dQsJKosKQWVcZiBSlRFBbmhzIocvHg8KQddV

🚀 config successfully set up!
You can manually modify it in: '/home/user/airlang/.airfold/config.yaml'
```

### Set up the monitoring pipeline

Push the pipeline project into you Airfold workspace:
```shell
af push ./airfold
```
List the sources:
```shell
                                    4 sources                                    
┌──────────────────────┬──────┬───────────┬────────┬──────────────┬──────────────┐
│ Name                 │ Rows │ Bytes     │ Errors │ Created      │ Updated      │
╞══════════════════════╪══════╪═══════════╪════════╪══════════════╪══════════════╡
│ aggregate_1min       │ 0    │ 0 Bytes   │ 0      │ a second ago │ a second ago │
├──────────────────────┼──────┼───────────┼────────┼──────────────┼──────────────┤
│ events               │ 0    │ 0 Bytes   │ 0      │ a second ago │ a second ago │
├──────────────────────┼──────┼───────────┼────────┼──────────────┼──────────────┤
│ high_processing_time │ 0    │ 0 Bytes   │ 0      │ a second ago │ a second ago │
├──────────────────────┼──────┼───────────┼────────┼──────────────┼──────────────┤
│ prices               │ 0    │ 0 Bytes   │ 0      │ a second ago │ a second ago │
└──────────────────────┴──────┴───────────┴────────┴──────────────┴──────────────┘
```

Add the pricing data to calculate costs:
```shell
af source append prices airfold/sources/prices.csv
```

### Send monitoring events

Run the supplied example script `main.py`
You will need two API keys: `OPENAI_API_KEY` and `AIRFOLD_API_KEY`

```shell
$ OPENAI_API_KEY=sk-111111111 \
AIRFOLD_API_KEY=aft_6eab8fcd902e4cbfb63ba174469989cd.Ds1PME5dQsJKosKQWVcZiBSlRFBbmhzIocvHg8KQddV \
python main.py

{
    "id": "chatcmpl-9S8rPT3uhmOFDaVyAnA5EEpSv9u50",
    "model": "gpt-4o",
    "group_id": "group01",
    "processing_time": 860,
    "req_tokens": 22,
    "resp_tokens": 35,
    "timestamp": 1716494271
}
$
```
_you can create a special `ingest` key for this task in your Airfold workspace_
