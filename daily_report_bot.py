import argparse
import re
import shutil
import tempfile
import threading
import time
from datetime import datetime
from pathlib import Path

import pyautogui
import pyperclip

PROJECT_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = PROJECT_DIR / "output"
CHROME_URL = "https://wttr.in/Chennai?format=3"

pyautogui.PAUSE = 0.2
pyautogui.FAILSAFE = True


class BotError(RuntimeError):
    pass


def open_chrome(url):
    profile_dir = Path(tempfile.mkdtemp(prefix="daily_report_chrome_"))
    pyautogui.hotkey("win", "r")
    time.sleep(1)
    command = (
        f'chrome --new-window --user-data-dir="{profile_dir}" '
        f'--no-first-run --no-default-browser-check --disable-background-mode "{url}"'
    )
    pyautogui.write(command, interval=0.002)
    pyautogui.press("enter")
    time.sleep(5)
    return profile_dir


def close_chrome(profile_dir):
    pyautogui.hotkey("alt", "f4")
    time.sleep(2)
    shutil.rmtree(profile_dir, ignore_errors=True)


def copy_page_text():
    pyautogui.hotkey("ctrl", "a")
    pyautogui.hotkey("ctrl", "c")
    time.sleep(0.5)
    text = pyperclip.paste()
    if not text.strip():
        raise BotError("Could not copy data from Chrome.")
    return text


def get_temperature(page_text):
    match = re.search(r"([+-]?\d+(?:\.\d+)?)\s*°?C\b", page_text, re.IGNORECASE)
    if not match:
        raise BotError("Could not find the temperature on the page.")
    return f"{match.group(1)}°C"


def open_calc(timeout=30):
    pyautogui.hotkey("win", "r")
    time.sleep(1)
    pyautogui.write("soffice --calc", interval=0.03)
    pyautogui.press("enter")

    deadline = time.time() + timeout
    while time.time() < deadline:
        for window in pyautogui.getAllWindows():
            title = window.title.strip().lower()
            if "libreoffice" in title and "calc" in title:
                try:
                    window.activate()
                except Exception:
                    pass
                time.sleep(2)
                return
        time.sleep(1)

    raise BotError("LibreOffice Calc did not become ready.")


def fill_report(timestamp, temperature):
    comment = "Warm conditions; stay hydrated."
    row = (
        "Date & Time\tFetched Data\tComment\n"
        f"{timestamp}\tChennai temperature: {temperature}\t{comment}"
    )
    pyautogui.hotkey("ctrl", "home")
    pyperclip.copy(row)
    pyautogui.hotkey("ctrl", "v")
    time.sleep(1)


def save_workbook(path):
    if path.exists():
        path.unlink()

    pyautogui.hotkey("ctrl", "shift", "s")
    time.sleep(2)
    pyautogui.hotkey("ctrl", "a")
    pyperclip.copy(str(path))
    pyautogui.hotkey("ctrl", "v")
    pyautogui.press("enter")
    time.sleep(3)

    for _ in range(3):
        pyautogui.press("enter")
        time.sleep(2)

    if not path.exists():
        raise BotError("LibreOffice Calc file was not saved.")


def close_calc():
    for window in pyautogui.getAllWindows():
        title = window.title.strip().lower()
        if "libreoffice" in title and "calc" in title:
            try:
                window.activate()
                time.sleep(0.5)
                pyautogui.hotkey("alt", "f4")
                time.sleep(2)
            except Exception:
                pass
            return


def save_screenshot(path):
    import mss
    from mss import tools

    time.sleep(1)
    with mss.mss() as sct:
        monitor = sct.monitors[1]
        screenshot = sct.grab(monitor)
        tools.to_png(screenshot.rgb, screenshot.size, output=str(path))


def save_fallback_report(timestamp, temperature, path):
    path.write_text(
        "Daily Weather Report\n\n"
        f"Date & Time: {timestamp}\n"
        f"Fetched Data: Chennai temperature: {temperature}\n"
        "Comment: Warm conditions; stay hydrated.\n",
        encoding="utf-8",
    )


def record_screen(path, stop_event, fps=5):
    import cv2
    import mss
    import numpy as np

    with mss.mss() as sct:
        monitor = sct.monitors[1]
        width = monitor["width"]
        height = monitor["height"]
        writer = cv2.VideoWriter(
            str(path),
            cv2.VideoWriter_fourcc(*"mp4v"),
            fps,
            (width, height),
        )
        delay = 1 / fps
        try:
            while not stop_event.is_set():
                started = time.time()
                frame = np.array(sct.grab(monitor))
                writer.write(cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR))
                time.sleep(max(0, delay - (time.time() - started)))
        finally:
            writer.release()


def run(record=False):
    OUTPUT_DIR.mkdir(exist_ok=True)
    today = datetime.now().strftime("%Y-%m-%d")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    spreadsheet_path = OUTPUT_DIR / f"daily_report_{today}.xlsx"
    fallback_path = OUTPUT_DIR / f"daily_report_{today}.txt"
    screenshot_path = OUTPUT_DIR / f"daily_report_{today}.png"
    video_path = OUTPUT_DIR / f"daily_report_{today}.mp4"

    stop_recording = threading.Event()
    recorder = None
    recording_started = None

    if record:
        recorder = threading.Thread(
            target=record_screen,
            args=(video_path, stop_recording),
            daemon=True,
        )
        recorder.start()
        recording_started = time.time()
        time.sleep(2)

    chrome_profile = None
    calc_open = False

    try:
        chrome_profile = open_chrome(CHROME_URL)
        page_text = copy_page_text()
        temperature = get_temperature(page_text)
        close_chrome(chrome_profile)
        chrome_profile = None

        try:
            open_calc()
            calc_open = True
            fill_report(timestamp, temperature)
            save_workbook(spreadsheet_path)
        except Exception as exc:
            save_fallback_report(timestamp, temperature, fallback_path)
            print(f"LibreOffice Calc step failed: {exc}")
            print(f"Fallback report created: {fallback_path}")

        save_screenshot(screenshot_path)

        if calc_open:
            close_calc()
            calc_open = False

        if record:
            elapsed = time.time() - recording_started
            time.sleep(max(0, 30 - elapsed))
    finally:
        if chrome_profile is not None:
            close_chrome(chrome_profile)
        if calc_open:
            close_calc()
        if record:
            stop_recording.set()
            recorder.join(timeout=5)

    if spreadsheet_path.exists():
        print(f"Spreadsheet: {spreadsheet_path}")
    if fallback_path.exists():
        print(f"Fallback: {fallback_path}")
    print(f"Screenshot: {screenshot_path}")
    if record:
        print(f"Recording: {video_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PyAutoGUI daily weather report bot")
    parser.add_argument(
        "--record",
        action="store_true",
        help="Record the desktop while the bot runs",
    )
    args = parser.parse_args()
    run(record=args.record)
