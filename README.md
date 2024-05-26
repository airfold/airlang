# Airlang

## ⚡ From Zero to Monitoring LLMs in 5 minutes ⚡

![Airlang](https://i.gyazo.com/024ef0910fe371a06da1250f0def5a70.png)

**⚡ 3 components: OpenAI, Streamlit, Airfold**

- [Install](#install)
- [Quick Start in 2 Minutes](#quick-start-in-2-minutes)
- [Let's ingest 1000 rows.](#lets-ingest-1000-rows)
- [Let's run the Streamlit dashboard](#lets-run-the-streamlit-dashboard)

## Install

Install requirements (ideally in a virtual environment):

```shell
pip install -r requirements.txt
```

## Quick Start in 2 Minutes
To get started we simply need to create a workspace in [Airfold](https://airfold.co) and retrieve an API key.
It's 100% free and takes less than a minute.


We use Airfold because it makes it so much easier to build real-time applications.


1. Go to [Airfold app](https://app.airfold.co/) and create a new workspace.

2. Press on the "Admin" token on the sidebar and copy it.
The token should look like this: `aft_6eab...KQvCddV`.

1. Then simply run `af config` in the project folder and paste the token:

```shell
$ af config
Configuring for API URL: https://api.airfold.co
? Api key: aft_6eab8...ocvKQddV

🚀 config successfully set up!
You can manually modify it in: '/home/user/airlang/.airfold/config.yaml'
```

4. Push the project to your Airfold workspace:
```shell
af push ./airfold
```

5. Add the pricing data to calculate costs:
```shell
af source append prices airfold/sources/prices.csv
```

Feel free to navigate to the UI and see all the sources and pipes you've pushed:
![Airfold UI](https://i.gyazo.com/ba6002386052831056d6597588c8d0db.png)


## Let's ingest 1000 rows.

Run the script `main.py`
You will need to set API keys: `OPENAI_API_KEY` and `AIRFOLD_API_KEY`

```shell
$ OPENAI_API_KEY=sk-xxxxxxxxx \
AIRFOLD_API_KEY=aft_6eab8f...QddV \
python main.py
```
![main.py](https://i.gyazo.com/f185d44504625d0f0a8869912fbc6e69.png)

## Let's run the Streamlit dashboard

Run the sample dashboard app:
```shell
AIRFOLD_API_KEY=aft_6eab8f...ddV \
streamlit run dashboard.py
```
