# PyAutoGUI - Daily Weather Report Bot

A lightweight PyAutoGUI desktop automation that collects the current Chennai temperature from a public web page, creates a daily weather report in LibreOffice Calc, saves a screenshot, and can record the desktop workflow.

The core automation is contained in `daily_report_bot.py`.

## Workflow

The bot:

1. Opens Chrome with a temporary browser profile.
2. Opens a public Chennai weather page.
3. Copies the page content and extracts the temperature.
4. Opens LibreOffice Calc.
5. Creates a row with the runtime date/time, fetched temperature, and a short weather comment.
6. Saves the workbook as `daily_weather_report_YYYY-MM-DD.xlsx`.
7. Captures a screenshot of the final report.
8. Optionally records the desktop workflow to an MP4 file.

If LibreOffice cannot be used, the bot creates a `.txt` fallback report containing the same information.

## Requirements

- Windows
- Python 3.10+
- Google Chrome
- LibreOffice

## 1. Open the project

Extract the project and open PowerShell in the project folder:

```powershell
cd daily-report-bot
```

## 2. Create the virtual environment

```powershell
python -m venv .venv
```

## 3. Activate the virtual environment

PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, use Command Prompt:

```cmd
.venv\Scripts\activate.bat
```

You should see `(venv)` at the beginning of the terminal prompt.

## 4. Install the libraries

```powershell
pip install -r requirements.txt
```

## 5. Run the bot

For a normal test run:

```powershell
python daily_report_bot.py
```

For a run that also creates a screen recording:

```powershell
python daily_report_bot.py --record
```

Do not move the mouse or type while the bot is running. PyAutoGUI is controlling the desktop.

## Output

Generated files are saved under `output/`:

```text
output/
├── daily_weather_report_YYYY-MM-DD.xlsx
├── daily_weather_report_YYYY-MM-DD.png
└── daily_weather_report_YYYY-MM-DD.mp4
```

The `.mp4` is created when `--record` is used. The `.txt` fallback is created only when LibreOffice cannot be used.

## Screen recording

The built-in recorder starts when the Python program starts and records the desktop workflow until it finishes.

A separate Windows screen recording can also be used to capture the terminal command and the complete workflow from the start.

## Chrome profile handling

The bot creates a temporary Chrome profile for each run instead of using the user's normal Chrome profile. This keeps personal tabs, cookies, extensions, and browsing data separate from the automation.

The temporary profile is removed after the browser workflow finishes.

## LibreOffice failure handling

The normal workflow uses LibreOffice Calc through PyAutoGUI.

If LibreOffice cannot start or the report cannot be saved, the bot creates a text report in `output/` containing the date/time, fetched temperature, and weather comment.

## Screen Recording

[Watch the automation demo](PyAutoGUI_Weather_Report_Bot_ScreenRecord.mp4)

## GitHub

The `output/` directory is used for generated files such as the report, screenshot, and recording.

The virtual environment and Python cache files are ignored by Git.

Do not place passwords, API keys, or other credentials in the project files.

## Notes

This project demonstrates desktop automation using PyAutoGUI, browser interaction, spreadsheet automation, file generation, screenshot capture, and optional desktop recording in a single workflow.

## License
This project is intended for personal learning and development purposes.
