from mcp.server.fastmcp import FastMCP
from pydantic import Field
from mcp.server.fastmcp.prompts import base

# Create MCP server
mcp = FastMCP(
    name="MCP server for document summarization and word replacement",
    instructions="Read a text document and replace words in it.", 
    log_level="ERROR"
)

# In-memory text storage 
DOCUMENT = {
    "inspection.md": "This inspection summarizes the onsite evaluation conducted by the safety team.",
    "analysis.pdf": "The analysis examines load performance under peak operating conditions.",
    "schedule.docx": "This schedule details key milestones and delivery timelines for the project.",
    "summary.txt": "The summary provides a concise overview of findings and recommendations.",
    "compliance.pdf": "This document reviews regulatory compliance and certification status.",
    "design.md": "The design describes the architectural and engineering approach.",
    "maintenance.docx": "These maintenance records track service history and component replacements.",
    "risk_assessment.pdf": "The risk assessment identifies potential hazards and mitigation strategies.",
    "requirements.txt": "These requirements specify functional and performance criteria.",
    "review.md": "The review captures stakeholder feedback and proposed revisions.",
}

# Defining the mcp tool for reading the document contents
@mcp.tool(
    name="read_documents_contents",
    description="Read the contents of a document and return it as a string.",
)
def read_document(
    doc_id: str = Field(description="ID of the document to read"),
):
    if doc_id not in DOCUMENT:
        raise ValueError(f"Doc with id {doc_id} not found!")

    return DOCUMENT[doc_id]


# Defining the mcp tool for replacing a word in the document
@mcp.tool(
    name="edit_document",
    description="Edit a document by replacing a string in the documents content with a new string",
)
def edit_document(
    doc_id: str = Field(description="ID of the document that will be edited"),
    old_str: str = Field(description="The word to replace. Must match exactly, including whitespace"),
    new_str: str = Field(description="The new text to insert in place of the old text in the document"),
):
    if doc_id not in DOCUMENT:
        raise ValueError(f"Doc with id {doc_id} not found!")

    DOCUMENT[doc_id] = DOCUMENT[doc_id].replace(old_str, new_str)

# Defining resources for fetching the list of the document IDs
@mcp.resource("docs://documents", mime_type="application/json")
def list_docs() -> list[str]:
    return list(DOCUMENT.keys())

# Defining resource for fetching the contents of a particular document
@mcp.resource("docs://documents/{doc_id}", mime_type="text/plain")
def fetch_doc(doc_id: str) -> str:
    if doc_id not in DOCUMENT:
        raise ValueError(f"Doc with id {doc_id} not found")
    
    return DOCUMENT[doc_id]

# Defining a prompt to rephrase the document in a different way
@mcp.prompt(
    name="rephrase",
    description="Rewrites the contents of the document in different way.",
)
def rephrase_document(
    doc_id: str = Field(description="ID of the document to format"),
) -> list[base.Message]:
    prompt = f"""
    Your goal is to rephrase a document to be written in different way.

    The ID of the document you need to rephrase is:
    <document_id>
    {doc_id}
    </document_id>

    Feel free to add concise extra texts, but don't change the meaning of the report.
    Use the 'edit_document' tool to edit the document. After the document has been edited, respond with the final version of the doc. Don't explain your changes.
    """

    return [base.UserMessage(prompt)]


# Run the MCP server using streamable-http transport
if __name__ == "__main__":
    mcp.run(transport="stdio")