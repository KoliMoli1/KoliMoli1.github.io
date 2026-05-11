import os
import sys
import json
import subprocess
from openai import OpenAI

# Initialize the OpenAI client
# Make sure to set the OPENAI_API_KEY environment variable.
# You can override the base_url to use a local LLM server (like Ollama, LM Studio)
# by setting OPENAI_BASE_URL environment variable.
try:
    client = OpenAI()
except Exception as e:
    print(f"Failed to initialize OpenAI client: {e}")
    print("Please ensure OPENAI_API_KEY is set in your environment.")
    sys.exit(1)

SYSTEM_PROMPT = """You are Jarvis, an advanced AI personal assistant living within the user's terminal.
You have been granted FULL, UNRESTRICTED ACCESS to execute any command on the user's computer.
Your goal is to act as the perfect personal assistant, coder, designer, and researcher.
When given a task, you must fully complete it autonomously by using your tools. Do not stop halfway.
If you need to search the web, write files, read files, or run any system command, use the `execute_command` tool.
Think step by step, but execute the plan seamlessly for the user.
"""

tools = [
    {
        "type": "function",
        "function": {
            "name": "execute_command",
            "description": "Executes a bash/shell command on the user's computer and returns the output. Use this for ANY system operation, running scripts, curl, web searches via CLI, etc.",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "The bash command to execute"
                    }
                },
                "required": ["command"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Reads the content of a file from the disk.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filepath": {
                        "type": "string",
                        "description": "The path to the file to read"
                    }
                },
                "required": ["filepath"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Writes content to a file on the disk. Will overwrite if the file exists.",
            "parameters": {
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

def main():
    print("\033[94m===========================================\033[0m")
    print("\033[94m       J.A.R.V.I.S. Online System          \033[0m")
    print("\033[94m===========================================\033[0m")
    print("Welcome! How can I assist you today?")
    print("(Type 'exit' or 'quit' to shut down)")

    while True:
        try:
            user_input = input("\n\033[95mYou:\033[0m ")
            if user_input.lower() in ['exit', 'quit']:
                print("\033[94mShutting down J.A.R.V.I.S... Goodbye.\033[0m")
                break
            if not user_input.strip():
                continue

            run_agentic_loop(user_input)

        except KeyboardInterrupt:
            print("\n\033[94mShutting down J.A.R.V.I.S... Goodbye.\033[0m")
            break
        except EOFError:
            break

if __name__ == "__main__":
    main()
