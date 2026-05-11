# KoliMoli1.github.io
A website that i designed, helps me a lot so i hope it helps you guys too

## J.A.R.V.I.S. Personal Assistant
This repository also contains **J.A.R.V.I.S.**, an advanced AI personal assistant living within your terminal. It has unrestricted access to execute any command, search the web, code, and perform tasks autonomously on your computer.

### Setup and Installation
1. Install Python 3.10+ (if not already installed).
2. Install the required dependencies:
   ```bash
   pip install openai
   ```
3. Set your OpenAI API key in your environment variables:
   ```bash
   export OPENAI_API_KEY="your-api-key-here"
   ```
   *Note: You can also use local LLMs (like Ollama or LM Studio) by setting the `OPENAI_BASE_URL` environment variable.*

### Running J.A.R.V.I.S.
Run the script to start the AI loop:
```bash
python jarvis.py
```
