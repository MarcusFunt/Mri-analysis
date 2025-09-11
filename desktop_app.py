"""Simple desktop GUI for the MRI Auto-Report demo.

This application provides a minimal yet functional interface for generating a
second-opinion report from a brain MRI study.  It calls into the existing agent
logic with stubbed AI models so it can run entirely offline as a demonstration.
"""

from __future__ import annotations

from pathlib import Path

import PySimpleGUI as sg

from agent.server import AnalyzeReq, analyze


# ---------------------------------------------------------------------------
# Application logic
# ---------------------------------------------------------------------------

def _run_analysis(study_dir: str) -> dict:
    """Execute the analysis pipeline and return the result structure."""

    req = AnalyzeReq(study_dir=study_dir, tools=[])
    return analyze(req)


# ---------------------------------------------------------------------------
# GUI setup
# ---------------------------------------------------------------------------

def main() -> None:
    sg.theme("SystemDefault")

    layout = [
        [sg.Text("MRI study folder"), sg.Input(key="-DIR-"), sg.FolderBrowse()],
        [sg.Button("Analyze", key="-RUN-")],
        [sg.Text("", key="-STATUS-")],
        [sg.Multiline(size=(80, 20), key="-OUT-", disabled=True)],
    ]

    window = sg.Window("MRI Second Opinion Demo", layout)

    while True:
        event, values = window.read()
        if event == sg.WINDOW_CLOSED:
            break
        if event == "-RUN-":
            study_dir = values.get("-DIR-", "")
            if not study_dir or not Path(study_dir).exists():
                sg.popup_error("Please choose a valid folder containing the study")
                continue
            window["-STATUS-"].update("Analyzing...")
            window.refresh()
            try:
                res = _run_analysis(study_dir)
            except Exception as e:  # pragma: no cover - GUI runtime
                window["-STATUS-"].update("Analysis failed")
                sg.popup_error("Analysis failed", str(e))
                continue
            window["-STATUS-"].update(
                "Normal" if res.get("normal") else "Abnormal"
            )
            out = (
                f"Study: {study_dir}\n"
                f"Confidence: {res.get('confidence', 0.0):.2f}\n\n"
                f"Impression:\n{res.get('impression', '')}\n\n"
                "Findings:\n" + "\n".join(f"- {f}" for f in res.get("findings", []))
            )
            window["-OUT-"].update(out)

    window.close()


if __name__ == "__main__":  # pragma: no cover - manual execution
    main()
