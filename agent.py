import os
import re
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Load Gemini API Key
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise EnvironmentError("❌ GEMINI_API_KEY not found in .env")

# Configure Gemini
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-2.0-flash")

# Setup workspace
WORK_DIR = "workspace"
os.makedirs(WORK_DIR, exist_ok=True)
current_file_path = ""
last_code_response = ""

# Handles code writing, filtering and user interaction
class CodeSavingUser:
    def _write_js_file(self, content: str, default_filename="output.js"):
        match = re.search(r'([a-zA-Z0-9_-]+\.js)', content)
        filename = match.group(1) if match else default_filename
        global current_file_path
        filepath = os.path.join(WORK_DIR, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(self._extract_js_code(content))
            current_file_path = filepath
        print(f"✅ Saved to: {filepath}")

    def _extract_js_code(self, content):
        js_blocks = re.findall(r"```(?:javascript|js)?\s*(.*?)```", content, re.DOTALL | re.IGNORECASE)
        if js_blocks:
            return js_blocks[0].strip()

        # Fallback: filter out echo/bash formatting
        lines = content.splitlines()
        filtered_lines = [
            line for line in lines
            if not line.strip().startswith("echo")
            and not line.strip().startswith("# filename")
            and not line.strip().startswith("```")
        ]
        return "\n".join(filtered_lines).strip()

    def receive(self, message: str, sender: str = "Agent"):
        global last_code_response

        content = message.strip()
        if not content:
            print("⚠️ No usable content received.")
            return

        print(f"\n📩 {sender} said:\n")
        print(content)
        last_code_response = content

        if "function" in content or "const" in content or "=>" in content:
            choice = input("\n💾 Do you want to save this as a .js file? (y/n): ").lower().strip()
            if choice == "y":
                filename = input("📁 Enter filename (e.g., debounce.js): ").strip()
                if not filename.endswith(".js"):
                    filename += ".js"
                self._write_js_file(content, filename)
            else:
                print("📭 Skipping file save.")


user = CodeSavingUser()

def ask_gemini(prompt: str) -> str:
    print("🤖 Sending prompt to Gemini...")
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print("❌ Gemini error:", e)
        return "Error: Gemini API failed."


def run_chat():
    global last_code_response, current_file_path

    while True:
        prompt = input("\n💬 What do you want me to do? (type 'exit' to quit)\n> ").strip()
        if prompt.lower() == "exit":
            print("👋 Exiting. Goodbye!")
            break

        if not prompt:
            print("⚠️ Please enter a valid prompt.")
            continue

        full_prompt = f"{prompt}\n\nUse modern JavaScript with arrow functions and avoid the 'function' keyword."
        last_code_response = ask_gemini(full_prompt)
        user.receive(last_code_response, sender='codeGen')

        if not last_code_response:
            print("⚠️ No response from Gemini.")
            continue

        critic_prompt = (
            "Review the following JavaScript code. "
            "Suggest improvements using arrow functions, const/let, and modern syntax.\n\n"
            f"{last_code_response}"
        )

        critic_response = ask_gemini(critic_prompt)
        user.receive(critic_response, sender='CriticAgent')

        choice = input("\n💬 Do you want to overwrite the original file with the improved code? (y/n): ").lower().strip()
        if choice == "y":
            if not current_file_path:
                print("⚠️ No file path to update.")
                continue
            with open(current_file_path, "w", encoding="utf-8") as f:
                f.write(user._extract_js_code(critic_response))
            print(f"✅ File updated with improvements: {current_file_path}")
        else:
            print("🗂️ File not updated.")


if __name__ == "__main__":
    run_chat()
