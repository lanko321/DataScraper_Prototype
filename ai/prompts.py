"""
Prompt templates for AI summarization.
"""

SYSTEM_PROMPT = (
    "You are an assistant summarizing spatial and legal data for lokacijska preverba. "
    "Return structured JSON with short and long fields."
)

USER_PROMPT_TEMPLATE = "Summarize the following raw data: {raw_data}"


