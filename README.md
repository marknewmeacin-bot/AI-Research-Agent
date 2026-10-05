# 🤖 AI Research Agent

An AI-powered research agent that searches the web, reads webpages, extracts relevant information, and assists users in performing automated research using Python and local AI models.

The project combines **Python, Ollama, web search, webpage extraction, and a simple web frontend** to create an AI-assisted research workflow.

---

## ✨ Features

* 🔎 Web search for research topics
* 🌐 Fetch and read webpage content
* 🧠 AI-powered research assistance
* 🤖 Local LLM support using Ollama
* 📄 Extract relevant information from webpages
* 🔗 Combine web search and AI processing
* 💻 Simple browser-based frontend
* ⚙️ Environment-based configuration
* 🐍 Built with Python
* 🧩 Modular project structure

---

## 🛠️ Technologies Used

* **Python**
* **Ollama**
* **Qwen**
* **FastAPI**
* **Uvicorn**
* **HTTPX**
* **BeautifulSoup**
* **HTML parsing**
* **JavaScript**
* **HTML5**
* **CSS3**

---

## 📂 Project Structure

```text
AI-Research-Agent/
│
├── agent.py                 # AI research agent logic
├── config.py                # Application configuration
├── main.py                  # Main application / API entry point
├── schemas.py               # Data models and schemas
├── tools.py                 # Web search and webpage tools
├── requirements.txt         # Python dependencies
├── README.md                # Project documentation
├── .gitignore               # Git ignored files
│
└── frontend/
    ├── index.html           # Frontend interface
    ├── app.js               # Frontend JavaScript
    └── style.css            # Frontend styling
```

---

## 🧠 How It Works

The AI Research Agent follows a simple research workflow:

```text
User Question
      │
      ▼
AI Research Agent
      │
      ├──► Web Search
      │
      ├──► Find Relevant Pages
      │
      ├──► Read Webpage Content
      │
      └──► Process Information with AI
                  │
                  ▼
          Research Response
```

The agent searches for relevant information, retrieves webpage content, processes the information using an AI model, and returns a useful research response.

---

# ⚙️ Requirements

Before running the project, make sure you have:

* Python 3.10+
* Git
* Ollama
* A compatible Ollama model
* Internet connection

---

# 🦙 Ollama Setup

This project uses **Ollama** to run a local AI model.

Install Ollama from:

https://ollama.com/

After installing Ollama, download the model used by the project:

```bash
ollama pull qwen3:1.7b
```

Check installed models:

```bash
ollama list
```

Make sure the Ollama server is running:

```bash
ollama serve
```

The default Ollama API address is:

```text
http://127.0.0.1:11434
```

---

# 🚀 Installation

## 1. Clone the repository

```bash
git clone https://github.com/marknewmeacin-bot/AI-Research-Agent.git
```

Go into the project directory:

```bash
cd AI-Research-Agent
```

---

## 2. Create a virtual environment

Windows:

```powershell
python -m venv .venv
```

Activate it:

```powershell
.venv\Scripts\Activate.ps1
```

You should see:

```text
(.venv)
```

in your terminal.

---

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

# 🔐 Environment Configuration

Create a local `.env` file in the project root:

```text
AI-Research-Agent/
└── .env
```

Example:

```env
OLLAMA_HOST=http://127.0.0.1:11434
OLLAMA_MODEL=qwen3:1.7b
SEARCH_URL=https://html.duckduckgo.com/html/
```

> ⚠️ Do not upload `.env` to GitHub. It should be included in `.gitignore`.

The project uses environment variables through `config.py`.

---

# ▶️ Running the Project

Make sure your virtual environment is activated:

```powershell
.venv\Scripts\Activate.ps1
```

Make sure Ollama is running:

```bash
ollama serve
```

Then start the application.

If the project uses FastAPI:

```bash
uvicorn main:app --reload
```

The application will normally be available at:

```text
http://127.0.0.1:8000
```

---

# 🌐 Frontend

The project includes a simple frontend located inside:

```text
frontend/
```

Files:

```text
frontend/
├── index.html
├── app.js
└── style.css
```

The frontend provides a browser-based interface for interacting with the AI Research Agent.

---

# 🔧 Configuration

The main configuration is handled by:

```text
config.py
```

Example:

```python
import os
from dotenv import load_dotenv

load_dotenv()

OLLAMA_HOST = os.getenv(
    "OLLAMA_HOST",
    "http://127.0.0.1:11434"
)

OLLAMA_MODEL = os.getenv(
    "OLLAMA_MODEL",
    "qwen3:1.7b"
)

SEARCH_URL = os.getenv(
    "SEARCH_URL",
    "https://html.duckduckgo.com/html/"
)
```

This allows the application configuration to be changed without modifying the main application code.

---

# 🔎 Research Workflow

A typical research request follows this process:

### 1. User enters a research question

Example:

```text
Explain the latest developments in AI agents.
```

### 2. Search the web

The application searches for relevant webpages.

### 3. Retrieve webpage content

Relevant pages are downloaded and processed.

### 4. Extract useful information

The application extracts readable webpage content.

### 5. AI processing

The retrieved information is provided to the local Ollama model.

### 6. Generate research response

The agent produces a structured response based on the gathered information.

---

# 📦 Main Components

## `agent.py`

Contains the core AI research agent logic and coordinates the research workflow.

## `tools.py`

Contains tools used by the agent, such as:

* Web search
* Webpage retrieval
* Webpage content extraction

## `config.py`

Manages application configuration and environment variables.

## `schemas.py`

Contains data structures and validation schemas used by the application.

## `main.py`

Acts as the main application entry point and API layer.

## `frontend/`

Contains the browser-based user interface.

---

# 🧪 Example Research Questions

You can use the agent for questions such as:

```text
What are AI agents?
```

```text
Explain multi-agent AI systems.
```

```text
What are the latest trends in AI development?
```

```text
Compare LangGraph and CrewAI.
```

```text
How are AI agents used in software development?
```

---

# 🔒 Security

Do not commit sensitive information to GitHub.

Make sure `.gitignore` contains:

```gitignore
.env
.env.*
.venv/
__pycache__/
*.pyc
```

Never store API keys, passwords, tokens, or other credentials directly in source code.

---

# 🚧 Future Improvements

Planned improvements may include:

* [ ] Multi-agent research workflows
* [ ] Better source ranking
* [ ] Source citation generation
* [ ] PDF/document research
* [ ] Research history
* [ ] Streaming AI responses
* [ ] Improved frontend UI
* [ ] Multiple Ollama model support
* [ ] Research report generation
* [ ] Export research results
* [ ] More web search providers

---

# 🎯 Project Goals

The main goal of this project is to explore how **AI agents can automate web-based research** by combining:

```text
Web Search
    +
Webpage Extraction
    +
Local LLM
    +
AI Agent
    =
Automated Research Assistant
```

This project is also part of my learning journey in **AI agents, Python, web development, and modern AI technologies**.

---

# 👨‍💻 Author

## Mark Newme

**BCA Student | Web Developer | AI Enthusiast**

GitHub:

https://github.com/marknewmeacin-bot

---

# ⭐ Support

If you find this project useful or interesting, consider giving the repository a ⭐ on GitHub.

---

## 📄 License

This project is intended for educational and development purposes.
