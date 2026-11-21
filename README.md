# RCCG Livestream Readiness Dashboard

A Streamlit checklist I made for the media team at RCCG so we can confirm the livestream is ready before service starts.

## What it does

- Checks that the PTZ camera and streaming PC are reachable over TCP
- Walks through the manual checks: Behringer X32 audio, vMix inputs, EasyWorship lyrics, with troubleshooting tips for each
- Shows Ready, Needs attention, or Checks incomplete
- Exports a CSV report with volunteer, service, results and notes

## Run it

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Open http://127.0.0.1:8501. Run it on a computer that is on the production network, enter each device's address and a port it listens on (the defaults, 80 and 445, are just examples).

A pass means a TCP connection worked from the computer running the dashboard. A failure can mean a wrong address, a closed port, or a firewall. To try it without any devices, point a check at `127.0.0.1` port `8501`.

Results live in the browser session, so download the CSV before refreshing.

## Stack

Python, Streamlit, `socket` and `csv` from the standard library
