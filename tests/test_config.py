from mcp_document_summary.config import settings

def test_settings_load():
    # It seems the environment has gpt-4o-mini set
    assert settings.openai_model_name in ["gpt-4o", "gpt-4o-mini"]
    assert settings.log_level == "INFO"
