import csv
import io
import socket
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

import streamlit as st

# Devices we ping over TCP, with a troubleshooting tip for each
DEVICES = (
    ("PTZ camera",
     "Check camera power or PoE, the switch link, and the camera IP and service port."),
    ("Streaming PC",
     "Wake the PC, check its Ethernet connection, and confirm the selected service is "
     "listening and allowed by the firewall."),
)

# Things a volunteer has to check by eye and ear: (name, what to do, troubleshooting)
CHECKLIST = (
    ("Behringer X32 audio", "Listen on the stream bus and confirm clean audio from a mic and playback.",
     "Check input gain, channel mute, bus sends and the output patch. Verify the returned signal on the streaming PC."),
    ("vMix inputs", "Preview the camera and media inputs and confirm audio meters respond.",
     "Check the capture or network source, reselect the input and confirm the intended audio source is enabled."),
    ("EasyWorship lyrics", "Preview a lyric slide and confirm it appears correctly in the stream preview.",
     "Verify the service schedule and destination display or capture source. Test the lyrics again in vMix preview."),
)


def check_device(endpoint):
    """Try a TCP connection to (host, port) and return (status, detail)."""
    host, port = endpoint
    if not host:
        return "Not configured", "Enter a hostname or IP address."
    try:
        with socket.create_connection((host, port), timeout=2):
            return "Pass", "TCP connection established."
    except OSError as error:
        return "Fail", error.strerror or str(error)


def make_report(generated, verdict, volunteer, service, observed, automatic, manual, notes):
    file = io.StringIO()
    writer = csv.writer(file)
    writer.writerow(("Report generated", "Readiness", "Volunteer", "Service", "Checked at",
                     "Type", "Check", "Target", "Result", "Detail", "Notes"))

    # Stops Excel from running a cell that starts with = + - or @ as a formula
    def safe(value):
        return "'" + value if value.lstrip().startswith(("=", "+", "-", "@")) or value.startswith(("\t", "\r", "\n")) else value

    for kind, checked, rows in (("TCP", observed, automatic), ("Manual", "", manual)):
        for name, target, status, detail in rows:
            writer.writerow(map(safe, (generated, verdict, volunteer, service, checked,
                                       kind, name, target, status, detail, notes)))
    return file.getvalue()


def main():
    st.set_page_config(page_title="RCCG Livestream Readiness", page_icon="🎥", layout="wide")
    st.caption("RCCG MEDIA TEAM")
    st.title("Livestream readiness")
    st.write("Run your network checks and walk through the production checklist before service.")
    sidebar = st.sidebar
    sidebar.header("Service details")
    service = sidebar.text_input("Service or event", max_chars=100)
    volunteer = sidebar.text_input("Volunteer", max_chars=100)
    sidebar.divider()
    sidebar.header("Device endpoints")
    sidebar.caption("Enter the address and a known listening TCP port for each device.")
    endpoints = []
    for index, (name, _) in enumerate(DEVICES):
        host = sidebar.text_input(f"{name} host", max_chars=253).strip()
        port = sidebar.number_input(f"{name} TCP port", 1, 65535, 80 if index == 0 else 445)
        endpoints.append((host, port))

    st.header("Network checks")
    st.caption("TCP checks run from the computer hosting this dashboard and measure reachability to the selected service port.")
    if st.button("Run network checks", type="primary", disabled=not any(host for host, _ in endpoints)):
        with st.spinner("Checking device endpoints…"):
            # run both checks at once so one slow device doesn't hold up the other
            with ThreadPoolExecutor(max_workers=len(DEVICES)) as pool:
                results = list(pool.map(check_device, endpoints))
        st.session_state.network = (endpoints, results, datetime.now().astimezone().isoformat(timespec="seconds"))
    # results are only valid if the addresses haven't been edited since the last run
    saved_endpoints, results, observed = st.session_state.get("network", ([], [], ""))
    automatic = []
    all_current = saved_endpoints == endpoints
    if all_current:
        st.caption(f"Last run {observed}")
    for index, (column, (name, help_text)) in enumerate(zip(st.columns(2), DEVICES)):
        host, port = endpoints[index]
        target = f"[{host}]:{port}" if ":" in host else f"{host}:{port}" if host else ""
        if not host:
            status, detail = "Not configured", "Enter a device host in the sidebar."
        elif all_current:
            status, detail = results[index]
        else:
            status, detail = "Not checked", "Run the network checks for the current endpoints."
        with column.container(border=True):
            st.subheader(name)
            if target:
                st.text(target)
            if status == "Pass":
                st.success(status)
            elif status == "Fail":
                st.error(status)
            else:
                st.info(status)
            st.text(detail)
            with st.expander("Troubleshooting"):
                st.write(help_text)
        automatic.append((name, target, status, detail))

    st.header("Production checklist")
    manual = []
    for name, instruction, troubleshooting in CHECKLIST:
        with st.container(border=True):
            st.subheader(name)
            st.write(instruction)
            status = st.radio(f"{name} result", ("Not checked", "Pass", "Fail"),
                              horizontal=True, label_visibility="collapsed")
            with st.expander("Troubleshooting"):
                st.write(troubleshooting)
        manual.append((name, "", status, instruction))

    st.header("Readiness report")
    notes = st.text_area("Notes and follow-up actions", max_chars=2000)
    # any failure wins, otherwise every check has to pass to be Ready
    statuses = [row[2] for row in automatic + manual]
    if "Fail" in statuses:
        verdict = "Needs attention"
        st.error(verdict)
    elif all(status == "Pass" for status in statuses):
        verdict = "Ready"
        st.success(verdict)
    else:
        verdict = "Checks incomplete"
        st.info(verdict)
    now = datetime.now().astimezone()
    report = make_report(now.isoformat(timespec="seconds"), verdict, volunteer, service,
                         observed if all_current else "", automatic, manual, notes)
    st.download_button("Download readiness report (CSV)", report,
                       f"rccg-readiness-{now:%Y-%m-%d}.csv", "text/csv", on_click="ignore")


if __name__ == "__main__":
    main()
