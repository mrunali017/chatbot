# Grok Chatbot

An interactive desktop chatbot built with Python 3.10+ and Tkinter, utilizing xAI's Grok API via the `requests` library.

## Project Structure
- `bot.py`: Main chatbot script implementing the Tkinter GUI and API logic.
- `requirements.txt`: Python package dependencies (`python-dotenv`, `requests`).
- `.env`: Environment variables configuration file for your API key.
- `README.md`: Setup and usage instructions.
- `run_chatbot.bat`: A batch script to easily launch the chatbot.

## Prerequisites
Ensure Python is installed on your system.

## Setup Instructions

1. **Configure API Key**
   Create a `.env` file in the root directory (or edit `dist/.env` if running the compiled executable) and add your actual xAI API key:
   ```env
   GROK_API_KEY=your_xai_api_key_here
   ```

2. **Activate the Virtual Environment**
   Navigate to the project root directory and activate the `"iisc env"` virtual environment:
   ```powershell
   & "iisc env/Scripts/Activate.ps1"
   ```

3. **Install Dependencies**
   Install the required libraries:
   ```powershell
   pip install -r requirements.txt
   ```

## Running the Chatbot

Start the chatbot with:
```powershell
python bot.py
```
Or double-click `run_chatbot.bat` on Windows.

### Exit Commands
To step out and exit the program, type either:
- `exit`
- `step out`
