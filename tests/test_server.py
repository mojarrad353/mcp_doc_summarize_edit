from mcp_document_summary.server.server import list_docs, fetch_doc, read_document, edit_document

def test_list_docs():
    docs = list_docs()
    assert len(docs) > 0
    assert "inspection.md" in docs

def test_fetch_doc():
    content = fetch_doc("inspection.md")
    assert "inspection" in content

def test_read_document():
    content = read_document("inspection.md")
    assert "inspection" in content

def test_edit_document():
    # Test editing a document (in memory)
    original_content = read_document("inspection.md")
    edit_document("inspection.md", "safety", "security")
    new_content = read_document("inspection.md")
    assert "security" in new_content
    assert "safety" not in new_content
    
    # Cleanup (revert change for other tests if needed, though in-memory persistence is acceptable for unit test sequence here)
    edit_document("inspection.md", "security", "safety")
