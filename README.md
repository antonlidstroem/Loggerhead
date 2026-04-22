# Loggerhead v1.3 - The Cleaner

Loggerhead is a lightweight Python-based utility designed to monitor, analyze, and clean log files in real-time. The application is specifically built to help developers identify errors and warnings in extensive log data by filtering out noise and formatting critical events with clear color coding.

## Core Features

* Real-time Monitoring: The program monitors selected files and updates the view automatically as new data is written to the disk.
* Log Washing: Built-in algorithms strip away long URLs and redundant tracking IDs to improve readability.
* Color-coded Analysis: Automatically identifies and highlights ERROR, WARNING, and INFO levels.
* Clipboard Support: Quickly paste log text directly from the clipboard for immediate analysis without the need to save a file.

## Installation

### Prerequisites
* Python 3.x installed.
* Pillow library (if logo support is enabled).

### Install Dependencies
To run the application with full visual functionality, install the Pillow library for image handling:

```bash
pip install Pillow
```

## Usage

1. Run the application:
   ```bash
   python loggerhead.py
   ```
2. Open File: Use the button to select a .log or .txt file. The program will immediately begin monitoring the file for changes.
3. Paste: If you have log data in your clipboard, use this button to clear the screen and display the new data.
4. Wash & Analyze: This function runs a regex-based process that simplifies the log by replacing noise with placeholders like [URL] and [ID].
5. Clear: Empties the terminal window and stops any ongoing file monitoring.

## Technical Configuration

### Color Coding
The application uses the following logic for visual categorization:
* Red (ERROR): Triggered by keywords such as FAIL, ERROR, 429, 500.
* Yellow (WARNING): Triggered by keywords such as WARNING, VIOLATES, INTERVENTION.
* Blue (INFO): Triggered by keywords such as INFO, XHR, FETCH.
* Purple (SYSTEM): Internal system messages from the application itself.

### File Requirements
For best results, log files should be encoded in UTF-8. The application handles character errors by ignoring invalid sequences to prevent crashes when reading binary data.

## Development and Customization

To add custom filtering rules, the `wash_log` method can be expanded with additional regular expressions (regex). The application logo can be updated by replacing `logo.png` in the root directory.

## License
This tool is provided as-is under the MIT License. You are free to use, modify, and distribute it.
```