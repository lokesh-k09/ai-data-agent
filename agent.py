import os
import subprocess
import re
import time
import random
import sys  # CRITICAL for Streamlit Cloud environment matching
import pandas as pd
import streamlit as st
from google import genai
from google.genai import types, errors
from dotenv import load_dotenv

# ---- Credential Management ----
if os.path.exists(".env"):
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
else:
    api_key = st.secrets.get("GEMINI_API_KEY")

client = genai.Client(api_key=api_key)

# Stable model alias
MODEL_NAME = 'models/gemini-2.5-flash'

def extract_code(text):
    pattern = r"```python\n(.*?)\n```"
    match = re.search(pattern, text, re.DOTALL)
    return match.group(1).strip() if match else None

def execute_code(code):
    script_name = f"temp_run_{random.randint(1000, 9999)}.py"
    try:
        with open(script_name, "w", encoding="utf-8") as f:
            # Pre-inject common imports for the agent's environment
            f.write("import pandas as pd\nimport matplotlib.pyplot as plt\nimport seaborn as sns\nimport yfinance as yf\nfrom scipy import stats\nimport os\n")
            f.write(code)
        
        # USE sys.executable TO ENSURE WE USE THE SAME VENV AS THE MAIN APP
        result = subprocess.run(
            [sys.executable, script_name], 
            capture_output=True, 
            text=True, 
            timeout=45
        )
        return result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return "", "Timeout Error: Execution exceeded the 45-second safety limit."
    except Exception as e:
        return "", f"System Error: {str(e)}"
    finally:
        if os.path.exists(script_name):
            try: os.remove(script_name)
            except: pass

def call_gemini_with_retry(contents, system_instruction):
    for i in range(5):
        try:
            return client.models.generate_content(
                model=MODEL_NAME,
                config=types.GenerateContentConfig(system_instruction=system_instruction),
                contents=contents
            )
        except errors.ClientError as e:
            if "429" in str(e) or "quota" in str(e).lower():
                time.sleep((2 ** i) + random.random())
                continue
            raise e
        except errors.ServerError as e:
            if "503" in str(e) or "unavailable" in str(e).lower():
                time.sleep((2 ** i) + random.random())
                continue
            raise e
    return None

def run_agent(user_prompt, filename=None):
    file_info = f"The user has uploaded a file named '{filename}'." if filename else "No file uploaded."
    
    SYSTEM_PROMPT = f"""
    You are a Senior Data Scientist Agent. 
    CONTEXT: {file_info}
    
    RULES:
    1. If a file is uploaded, use pd.read_csv('{filename}') ONLY after checking os.path.exists().
    2. Wrap all Python code in ```python blocks.
    3. yfinance: Use `auto_adjust=True`. 
       IMPORTANT: For multiple tickers, yfinance returns a MultiIndex. 
       Always flatten them using: `df.columns = df.columns.get_level_values(0)` 
       OR access them specifically like `df['Close']['MSFT']`.
    4. Use 'Close' instead of 'Adj Close'.
    5. Save all plots to 'output_plot.png' using `plt.savefig()`. NEVER use plt.show().
    6. You MUST print() statistical results so they appear in stdout.
    7. Provide a concise interpretation after code execution.
    """

    history = [types.Content(role="user", parts=[types.Part.from_text(text=user_prompt)])]
    
    for attempt in range(3):
        response = call_gemini_with_retry(history, SYSTEM_PROMPT)
        if not response:
            return "Error: API Quota exhausted."

        code = extract_code(response.text)
        if not code:
            return response.text 

        stdout, stderr = execute_code(code)
        
        if not stderr or (stdout and "Error" not in stderr):
            interpretation_prompt = f"Code executed successfully. Output:\n{stdout}\n\nInterpret these results."
            history.append(types.Content(role="model", parts=[types.Part.from_text(text=response.text)]))
            history.append(types.Content(role="user", parts=[types.Part.from_text(text=interpretation_prompt)]))
            
            final_interpretation = call_gemini_with_retry(history, SYSTEM_PROMPT)
            summary = final_interpretation.text if final_interpretation else "Analysis complete."
            return f"### Results\n{stdout}\n\n### Summary\n{summary}"
        else:
            history.append(types.Content(role="model", parts=[types.Part.from_text(text=response.text)]))
            history.append(types.Content(role="user", parts=[types.Part.from_text(text=f"EXECUTION ERROR:\n{stderr}\n\nFix the code and try again.")]))
            time.sleep(1)

    return f"**Error: The agent failed after 3 attempts.**\n\n**Last Code Error:**\n```python\n{stderr}\n```"