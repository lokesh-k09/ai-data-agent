# 🤖 Agentic AI Data Analyst
### CISC 520: Data Engineering & Data Science Final Project

**Live Application**: [https://ai-data-agent-gfgtb5dfk4fbtgvdndatwk.streamlit.app/](https://ai-data-agent-gfgtb5dfk4fbtgvdndatwk.streamlit.app/)

An autonomous AI-powered web application designed to bridge the gap between natural language and complex data science. This system uses Large Language Models (LLMs) to plan, write, execute, and interpret Python code in real-time, providing an end-to-end "Agentic" experience for data exploration.

## 🚀 Key Features
* **Autonomous Pipeline**: Implements a complete "Plan → Code → Execute → Interpret" workflow.
* **Self-Correction (Scenario D)**: The agent autonomously detects runtime errors (e.g., FileNotFoundError, KeyError), analyzes the traceback, and regenerates corrected code without user intervention.
* **Financial Analytics (Scenario A)**: Real-time stock data ingestion via `yfinance`, statistical summaries (mean, std dev, volatility), and trend visualization.
* **Dynamic CSV Exploration (Scenario B)**: Intelligent analysis of uploaded datasets with automatic column identification, missing value reporting, and distribution plotting.
* **Statistical Comparison (Scenario C)**: Advanced comparison logic for multiple entities, including t-tests and correlation analysis.
* **Safety Sandbox**: Execution is confined to a subprocess with a mandatory 45-second hardware timeout to ensure system stability.

## 🛠️ System Architecture
* **Frontend**: Developed using **Streamlit**, providing a conversational chat interface and dynamic file management.
* **Orchestration Layer**: A robust Python backend utilizing the **Google GenAI SDK** to manage conversation state and iterative agentic loops.
* **LLM Integration**: Powered by **Google Gemini 2.5 Flash** for high-speed reasoning and accurate code generation.
* **Execution Sandbox**: Uses a subprocess-based approach to execute generated code, capturing `stdout` and `stderr` to feed back into the agent for self-correction.

## 📦 Setup & Installation
1.  **Clone the Repository**:
    ```bash
    git clone [https://github.com/lokesh-k09/ai-data-agent.git](https://github.com/lokesh-k09/ai-data-agent.git)
    cd ai-data-agent
    ```
2.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
3.  **Configure Environment**:
    * Create a `.env` file in the root directory.
    * Add your Gemini API Key: `GEMINI_API_KEY=your_actual_key_here`.
    * (Refer to `.env.example` for the required format).
4.  **Run the Application**:
    ```bash
    streamlit run app.py
    ```

## 📝 Example Prompts
* **Financial**: "Fetch the last 100 days of AAPL stock prices. Plot a line chart and show the mean and standard deviation."
* **Data Analysis**: "Analyze the uploaded Air_Quality.csv. List the top 5 locations with the highest Ozone levels and show a bar chart."
* **Agentic Fix**: "Calculate the average of the 'AirQualityIndex' column." (The agent will realize the column name is wrong and fix it to 'Data Value' automatically).

## ⚠️ Safety & Reliability
* **Resource Guard**: All code executions are capped at 45 seconds to prevent infinite loops.
* **Credential Security**: API keys are managed exclusively via environment variables and are excluded from version control.
* **Rate Limiting**: Implements exponential backoff to handle Gemini API `429 RESOURCE_EXHAUSTED` errors gracefully.