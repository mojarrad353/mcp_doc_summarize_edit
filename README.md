# 📄 MCP For Document Summarization & Editing

![Python](https://img.shields.io/badge/Python-3.x-blue)
![MCP](https://img.shields.io/badge/MCP-FastMCP-success)

---

## 📌 Project Overview

The **MCP For Document Summarization & Editing** is a **Python-based MCP server** that enables users to interact with documents via a **command-line interface (CLI)**.

The project demonstrates:
- Building an MCP server using **FastMCP**
- Reading document contents programmatically
- Summarizing or rephrasing documents
- Replacing specific words or phrases based on user requests
- Handling CLI-driven interactions with MCP tools, resources, and prompts

---

## 🚀 Features

- 📖 Read document contents by document ID  
- ✏️ Replace words or phrases in documents  
- 📝 Summarize or rephrase documents without changing meaning  
- 🧰 MCP tools for document reading and editing  
- 📦 MCP resources for listing and fetching documents  
- 💻 CLI-based user interaction
- 🔹 Use @ in CLI to show all available documents
- 🔹 Use \ in CLI to view the already written rephrase prompt
---

## 🧑‍💻 Skills & Technologies

- **Programming Language:** Python  
- **Protocol:** Model Context Protocol (MCP)  
- **Framework:** FastMCP   
- **Interface:** Command-Line Interface (CLI)

---

## ▶️ How to Run the Project

1. **Clone the repository:**
git clone https://github.com/mojarrad353/mcp-doc-summarize-edit.git

2. **Start the MCP server:**
uv run mcp_server.py

3. **In a new terminal, run the CLI client:**
uv run main.py

