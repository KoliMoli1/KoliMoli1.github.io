# KoliMoli1.github.io
A website that i designed, helps me a lot so i hope it helps you guys too

## J.A.R.V.I.S. Personal Assistant
This repository also contains **J.A.R.V.I.S.**, an advanced AI personal assistant living within your terminal. It has unrestricted access to execute any command, search the web, code, and perform tasks autonomously on your computer.

### Setup and Installation
1. Install system dependencies for audio (on Ubuntu/Debian):
   ```bash
   sudo apt-get update && sudo apt-get install -y portaudio19-dev python3-tk espeak
   ```
2. Install Python 3.10+ (if not already installed).
3. Install the required Python dependencies:
   ```bash
   pip install anthropic google-genai SpeechRecognition pyttsx3 pyaudio
   ```
4. Set your API key in your environment variables. Jarvis uses Anthropic (Claude) by default:
   ```bash
   export ANTHROPIC_API_KEY="your-anthropic-api-key-here"
   ```
   *Alternatively, you can use Gemini:*
   ```bash
   export JARVIS_PROVIDER="gemini"
   export GEMINI_API_KEY="your-gemini-api-key-here"
   ```

### Running J.A.R.V.I.S.
Run the script to start the J.A.R.V.I.S. futuristic UI overlay:
```bash
python jarvis.py
```
To run purely in the terminal CLI without the UI, use:
```bash
python jarvis.py --cli
```
