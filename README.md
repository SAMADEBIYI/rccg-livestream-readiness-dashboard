# RCCG Livestream Readiness Dashboard

A Streamlit dashboard for pre-service connectivity checks, production checklists, and CSV readiness reports.

## Run locally

Use Python 3.11 or newer. Run these commands from the project root.

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

On Windows PowerShell, use `py -m venv .venv` and `.venv\Scripts\Activate.ps1`.

```sh
python -m streamlit run app.py --server.address 127.0.0.1
```

Open http://127.0.0.1:8501. Run Streamlit on a computer that can reach the production network. Enter the PTZ camera and streaming PC addresses and substitute known listening TCP ports. The initial port values (80 and 445) are examples. A pass confirms a TCP connection from the Streamlit host. A failure can indicate an incorrect address, a closed port, a firewall rule, or a network problem.

1. Enter the service and volunteer details, then run the device checks.
2. Mark Pass or Fail after verifying X32 audio, vMix inputs, and EasyWorship lyrics. Expand Troubleshooting for steps specific to each check.
3. Add follow-up notes and download the CSV. The dashboard reports Ready after all five checks pass. Any failure flags Needs attention.

Current results and notes live in the browser session. Download the report before refreshing or closing the tab. For a local walkthrough, point a device check at `127.0.0.1` port `8501` while Streamlit is running. That tests the dashboard's TCP probe against Streamlit itself.
