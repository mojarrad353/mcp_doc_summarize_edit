# 📄 MCP For Document Summarization & Editing

![Python](https://img.shields.io/badge/Python-3.x-blue)
![MCP](https://img.shields.io/badge/MCP-FastMCP-success)

---

The **MCP For Document Summarization & Editing** is a **Python-based MCP server** that enables users to interact with documents via a **command-line interface (CLI)**.

## Features

- **Document Management**: Read, list, and edit documents.
- **MCP Server**: FastMCP implementation.
- **OpenAI Integration**: Summarize and rephrase documents using OpenAI models.
- **CLI Chat**: Interactive command-line interface.
- **Docker Support**: Containerized for easy deployment.

## Project Structure

```text
mcp_doc_summarize_edit/
├── src/
│   └── mcp_document_summary/
│       ├── client/         # Client implementation
│       ├── core/           # Core logic (Chat, OpenAI, CLI)
│       ├── server/         # MCP Server implementation
│       ├── config.py       # Configuration settings
│       ├── logger.py       # Logging
│       └── main.py         # Entry point
├── tests/                  # Unit tests
├── Dockerfile
├── docker-compose.yml
├── docker-compose.yml
├── pyproject.toml
└── README.md
```

## Prerequisites

- Python 3.10+
- `uv` (required)
- OpenAI API Key

## Setup

1. **Clone the repository**
2. **Configure Environment**
   Copy `.env.example` to `.env` and fill in your details:
   ```bash
   cp .env.example .env
   ```
   Edit `.env` with your `OPENAI_API_KEY`.

3. **Install Dependencies**
   Using `uv`:
   ```bash
   uv sync
   ```

## Running the Application

### Local Development

1. **Start the MCP Server** (Terminal 1)
   ```bash
   uv run python -m mcp_document_summary.server.server
   ```
   The server will start on `http://127.0.0.1:8000`.

2. **Start the Client** (Terminal 2)
   ```bash
   uv run python -m mcp_document_summary.main --url http://127.0.0.1:8000/sse
   ```

### Docker
Run with Docker Compose:
```bash
docker-compose up --build
```

## Testing

Run unit tests:
```bash
uv run pytest
```

## Configuration

Settings are managed via `.env` file and `src/mcp_document_summary/config.py`.
- `OPENAI_API_KEY`: Your OpenAI API key.
- `OPENAI_MODEL_NAME`: Model to use (default: gpt-4o).
- `LOG_LEVEL`: Logging level (default: INFO).

## License

[License]
