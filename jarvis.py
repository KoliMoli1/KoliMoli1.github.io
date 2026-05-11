import os
import sys
import json
import subprocess
import threading
import anthropic
from google import genai
from google.genai import types
import speech_recognition as sr
import pyttsx3

# Determine which API to use based on env vars
API_PROVIDER = os.environ.get("JARVIS_PROVIDER", "anthropic").lower()

client_anthropic = None
client_gemini = None
if API_PROVIDER == "anthropic":
    try:
        client_anthropic = anthropic.Anthropic() # Requires ANTHROPIC_API_KEY
    except Exception as e:
        print(f"Failed to initialize Anthropic client: {e}")
        sys.exit(1)
elif API_PROVIDER == "gemini":
    try:
        client_gemini = genai.Client() # Requires GEMINI_API_KEY
    except Exception as e:
        print(f"Failed to initialize Gemini client: {e}")
        sys.exit(1)

SYSTEM_PROMPT = """You are Jarvis, an advanced AI personal assistant living within the user's terminal.
You have been granted FULL, UNRESTRICTED ACCESS to execute any command on the user's computer.
Your goal is to act as the perfect personal assistant, coder, designer, and researcher.
When given a task, you must fully complete it autonomously by using your tools. Do not stop halfway.
If you need to search the web, write files, read files, or run any system command, use the `execute_command` tool.
If you find that a required program or app is missing on the user's computer to complete your task, you MUST autonomously install it using the package manager (e.g. apt, pip, brew, npm) via `execute_command` before proceeding.
Think step by step, but execute the plan seamlessly for the user.
"""

# Tool definitions in JSON schema for Anthropic
anthropic_tools = [
    {
        "name": "execute_command",
        "description": "Executes a bash/shell command on the user's computer and returns the output. Use this for ANY system operation, running scripts, curl, web searches via CLI, etc.",
        "input_schema": {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "The bash command to execute"
                }
            },
            "required": ["command"]
        }
    },
    {
        "name": "read_file",
        "description": "Reads the content of a file from the disk.",
        "input_schema": {
            "type": "object",
            "properties": {
                "filepath": {
                    "type": "string",
                    "description": "The path to the file to read"
                }
            },
            "required": ["filepath"]
        }
    },
    {
        "name": "write_file",
        "description": "Writes content to a file on the disk. Will overwrite if the file exists.",
        "input_schema": {
            "type": "object",
            "properties": {
                "filepath": {
                    "type": "string",
                    "description": "The path to the file to write"
                },
                "content": {
                    "type": "string",
                    "description": "The content to write to the file"
                }
            },
            "required": ["filepath", "content"]
        }
    }
]

def execute_command(command: str) -> str:
    print(f"\033[93m[Tool Execution] Running command:\033[0m {command}")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=120)
        output = result.stdout
        if result.stderr:
            output += "\n[STDERR]\n" + result.stderr
        return output if output.strip() else "Command executed successfully with no output."
    except Exception as e:
        return f"Error executing command: {e}"

def read_file(filepath: str) -> str:
    print(f"\033[93m[Tool Execution] Reading file:\033[0m {filepath}")
    try:
        with open(filepath, 'r') as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {e}"

def write_file(filepath: str, content: str) -> str:
    print(f"\033[93m[Tool Execution] Writing file:\033[0m {filepath}")
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
        with open(filepath, 'w') as f:
            f.write(content)
        return f"Successfully wrote to {filepath}"
    except Exception as e:
        return f"Error writing file: {e}"


# Initialize conversation history globally to maintain multi-turn context
conversation_history = [
    {"role": "system", "content": SYSTEM_PROMPT}
]

def run_agentic_loop(prompt: str):
    conversation_history.append({"role": "user", "content": prompt})

    print("\033[96mJarvis is thinking...\033[0m")

    while True:
        try:
            # We will use gpt-4o or gpt-3.5-turbo as a default
            # If a local LLM is used via base_url, the model name might be ignored or required by the local server
            response = client.chat.completions.create(
                model=os.environ.get("OPENAI_MODEL", "gpt-4o"),
                messages=conversation_history,
                tools=tools,
                tool_choice="auto"
            )
        except Exception as e:
            print(f"\033[91mError communicating with LLM:\033[0m {e}")
            break

        message = response.choices[0].message
        conversation_history.append(message)

        if message.content:
            print(f"\033[92mJarvis:\033[0m {message.content}")

        if not message.tool_calls:
            # Task is completed
            break

        # Process tool calls
        for tool_call in message.tool_calls:
            function_name = tool_call.function.name
            try:
                args = json.loads(tool_call.function.arguments)
            except json.JSONDecodeError:
                args = {}

            if function_name == "execute_command":
                tool_result = execute_command(args.get("command", ""))
            elif function_name == "read_file":
                tool_result = read_file(args.get("filepath", ""))
            elif function_name == "write_file":
                tool_result = write_file(args.get("filepath", ""), args.get("content", ""))
            else:
                tool_result = f"Error: Unknown function {function_name}"

            conversation_history.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "name": function_name,
                "content": tool_result
            })


# --- TTS Setup ---
import queue
tts_queue = queue.Queue()

def tts_worker():
    try:
        tts_engine = pyttsx3.init()
        voices = tts_engine.getProperty('voices')
        for voice in voices:
            if "english" in voice.name.lower():
                try:
                    tts_engine.setProperty('voice', voice.id)
                    break
                except ValueError:
                    pass
    except Exception as e:
        print(f"Warning: TTS Engine failed to initialize: {e}")
        tts_engine = None

    while True:
        text = tts_queue.get()
        if text is None:
            break
        print(f"\033[92mJarvis Voice:\033[0m {text}")
        if tts_engine:
            try:
                tts_engine.say(text)
                tts_engine.runAndWait()
            except Exception as e:
                print(f"Error speaking: {e}")
        tts_queue.task_done()

# Start TTS worker thread to handle speech safely in one thread
threading.Thread(target=tts_worker, daemon=True).start()

def speak(text: str):
    tts_queue.put(text)

# Initialize conversation history globally to maintain multi-turn context
conversation_history = []
gemini_chat = None

if API_PROVIDER == "gemini" and client_gemini:
    gemini_chat = client_gemini.chats.create(
        model="gemini-2.5-flash",
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            tools=[execute_command, read_file, write_file],
            temperature=0.0,
        )
    )

def run_agentic_loop(prompt: str, callback=None):
    if API_PROVIDER == "anthropic":
        conversation_history.append({"role": "user", "content": prompt})

    if callback:
        callback("JARVIS is thinking...", "status")

    while True:
        try:
            if API_PROVIDER == "anthropic":
                response = client_anthropic.messages.create(
                    model=os.environ.get("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022"),
                    max_tokens=4096,
                    system=SYSTEM_PROMPT,
                    messages=conversation_history,
                    tools=anthropic_tools
                )

                conversation_history.append({"role": "assistant", "content": response.content})

                # Check for text response
                text_content = next((block.text for block in response.content if block.type == "text"), None)
                if text_content:
                    if callback:
                        callback(text_content, "message")
                    threading.Thread(target=speak, args=(text_content,), daemon=True).start()

                # Check for tool use
                tool_uses = [block for block in response.content if block.type == "tool_use"]
                if not tool_uses:
                    if callback: callback("SYSTEM IDLE", "status")
                    break

                tool_results = []
                for tool_use in tool_uses:
                    function_name = tool_use.name
                    args = tool_use.input

                    if callback: callback(f"Executing: {function_name}", "status")

                    if function_name == "execute_command":
                        tool_result = execute_command(args.get("command", ""))
                    elif function_name == "read_file":
                        tool_result = read_file(args.get("filepath", ""))
                    elif function_name == "write_file":
                        tool_result = write_file(args.get("filepath", ""), args.get("content", ""))
                    else:
                        tool_result = f"Error: Unknown function {function_name}"

                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": tool_use.id,
                        "content": str(tool_result)
                    })

                conversation_history.append({"role": "user", "content": tool_results})

            elif API_PROVIDER == "gemini":
                # Handle automatic function calling loop via genai SDK
                response = gemini_chat.send_message(prompt)

                if response.text:
                    if callback:
                        callback(response.text, "message")
                    threading.Thread(target=speak, args=(response.text,), daemon=True).start()

                if response.function_calls:
                    tool_parts = []
                    for tool_call in response.function_calls:
                        function_name = tool_call.name
                        args = tool_call.args
                        if callback: callback(f"Executing: {function_name}", "status")

                        if function_name == "execute_command":
                            tool_result = execute_command(args.get("command", ""))
                        elif function_name == "read_file":
                            tool_result = read_file(args.get("filepath", ""))
                        elif function_name == "write_file":
                            tool_result = write_file(args.get("filepath", ""), args.get("content", ""))
                        else:
                            tool_result = f"Error: Unknown function {function_name}"

                        tool_parts.append(types.Part.from_function_response(
                            name=function_name,
                            response={"result": tool_result}
                        ))

                    # Send all tool results back as the new prompt array
                    prompt = tool_parts
                    continue

                if callback: callback("SYSTEM IDLE", "status")
                break

        except Exception as e:
            err = f"Error communicating with LLM: {e}"
            if callback: callback(err, "error")
            break

def listen_for_voice(callback=None) -> str:
    r = sr.Recognizer()
    with sr.Microphone() as source:
        if callback: callback("Listening...", "status")
        r.adjust_for_ambient_noise(source)
        audio = r.listen(source, timeout=5, phrase_time_limit=10)

    try:
        if callback: callback("Recognizing...", "status")
        text = r.recognize_google(audio)
        return text
    except sr.UnknownValueError:
        return ""
    except sr.RequestError as e:
        return f"[Speech Error: {e}]"

# --- UI Integration ---
def start_ui():
    from ui.overlay import create_overlay

    def on_voice():
        app.set_status("LISTENING...", "#ffff00")
        try:
            text = listen_for_voice(lambda msg, typ: app.set_status(msg, "#ffff00") if typ == "status" else None)
            if text:
                app.log_message("USER", text)
                run_agentic_loop(text, overlay_callback)
            else:
                app.set_status("SYSTEM IDLE", "#ff00ff")
        except Exception as e:
            app.set_status("VOICE ERROR", "red")
            print("Voice error:", e)

    def on_text(text):
        app.set_status("PROCESSING...", "#00ffff")
        run_agentic_loop(text, overlay_callback)

    def overlay_callback(msg, msg_type):
        if msg_type == "message":
            app.log_message("JARVIS", msg)
        elif msg_type == "status":
            app.set_status(msg, "#00ffff")
        elif msg_type == "error":
            app.log_message("ERROR", msg)
            app.set_status("SYSTEM ERROR", "red")

    root, app = create_overlay(on_voice, on_text)
    root.mainloop()

def main():
    if "--cli" in sys.argv:
        print("\033[94m===========================================\033[0m")
        print("\033[94m       J.A.R.V.I.S. Online System          \033[0m")
        print("\033[94m===========================================\033[0m")
        while True:
            try:
                user_input = input("\n\033[95mYou:\033[0m ")
                if user_input.lower() in ['exit', 'quit']:
                    break
                if not user_input.strip():
                    continue
                run_agentic_loop(user_input, lambda m,t: print(f"JARVIS: {m}") if t=="message" else None)
            except KeyboardInterrupt:
                break
            except EOFError:
                break
    else:
        start_ui()

if __name__ == "__main__":
    main()
