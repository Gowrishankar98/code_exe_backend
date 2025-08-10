import os
import re
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Load Gemini API Key
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise EnvironmentError("❌ GEMINI_API_KEY not found in .env")

# Configure Gemini
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-2.0-flash")

# Workspace setup
WORK_DIR = "workspace"
os.makedirs(WORK_DIR, exist_ok=True)

# In-memory state
current_file_path = ""
last_code_response = ""


class CodeSavingUser:
    """Handles saving, extracting, and processing JS code"""

    def _write_js_file(self, content: str, filename="output.js"):
        """Save JavaScript content into a file."""
        global current_file_path
        filepath = os.path.join(WORK_DIR, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(self._extract_js_code(content))
        current_file_path = filepath
        print(f"✅ Saved to: {filepath}")
        return filepath

    def _extract_js_code(self, content: str):
        """
        Extracts ONLY the JavaScript code from Markdown/code fences.
        If no fenced code found, tries to guess code lines and filters out explanations.
        """
        # Try to match code block between triple backticks
        match = re.search(r"``````", content, re.IGNORECASE)
        if match:
            return match.group(1).strip()

        # Fallback: keep only likely code lines, strip explanations
        code_lines = []
        for line in content.splitlines():
            if (
                not line.strip()  # empty line
                or line.strip().startswith("#")      # markdown heading
                or line.strip().startswith("*")      # bullet points
                or line.strip().startswith(">")      # blockquote
                or line.strip().startswith("```")    # code fence markers
                or line.strip().lower().startswith("explanation")  # explanation label
                or re.match(r"^[A-Za-z\s]+:$", line.strip())       # section titles like "Example:"
                or re.match(r"^[\s\-\*]*[A-Za-z\s]{6,}[\.?!]$", line.strip())  # prose sentence
                or line.lower().strip().startswith("the above code")
            ):
                continue
            code_lines.append(line)
        return "\n".join(code_lines).strip()

    def receive(self, message: str, sender: str = "Agent", auto_save=False, filename="output.js"):
        """Receive a message (could be code), optionally auto-save."""
        global last_code_response
        content = message.strip()
        if not content:
            print("⚠️ No usable content received.")
            return None

        print(f"\n📩 {sender} said:\n")
        print(content)
        last_code_response = content

        if auto_save and (("function" in content) or ("const" in content) or ("=>" in content)):
            return self._write_js_file(content, filename)
        return None


user = CodeSavingUser()


def ask_gemini(prompt: str) -> str:
    """Send a prompt to Gemini and return its response text."""
    print("🤖 Sending prompt to Gemini...")
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print("❌ Gemini error:", e)
        return "Error: Gemini API failed."


def improve_code(js_code: str) -> str:
    """Ask Gemini to improve JavaScript code."""
    critic_prompt = (
        "Review the following JavaScript code. "
        "Suggest improvements using arrow functions, const/let, and modern syntax.\n\n"
        f"{js_code}"
    )
    return ask_gemini(critic_prompt)


# ---------------------
# Public API for Extension
# ---------------------

def process_prompt(prompt: str, auto_save=False, filename="output.js"):
    """
    Main entry point for extension.
    Sends ONLY the user prompt to Gemini (no modifications).
    Saves file if auto_save=True.
    Returns dictionary with details.
    """
    global last_code_response, current_file_path

    generated = ask_gemini(prompt)
    saved_path = user.receive(generated, sender="CodeGen", auto_save=auto_save, filename=filename)

    return {
        "original": generated,
        "file_path": saved_path or None
    }


def improve_js_code(js_code: str, auto_save=False, filename="output.js"):
    """
    Improves the provided JS code using Gemini.
    Runs ONLY when explicitly called.
    Optionally saves file if auto_save=True.
    """
    improved_code = improve_code(js_code)
    saved_path = None
    if auto_save:
        saved_path = user._write_js_file(improved_code, filename)
    user.receive(improved_code, sender="CriticAgent")
    return {
        "improved": improved_code,
        "file_path": saved_path
    }
