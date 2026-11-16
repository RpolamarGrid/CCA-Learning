"""
Task Statement 1.3 — Document Analysis Subagent

Same isolation principle as the web search subagent: fresh context, only
knows what's in its prompt. Uses a local `read_document` tool (our own
tool_executor, not a server-side tool) and runs through the SAME agentic
loop from Task 1.1 (stop_reason-driven), since this subagent must call a
tool and then reason about the result before finishing.

Output contract: structured findings with document_name + page_number
metadata, mirroring the web search subagent's source_url/source_title shape —
this consistency is what lets the coordinator merge both into one synthesis
prompt without losing attribution.
"""

import json
from pathlib import Path

from agentic_loop import run_agentic_loop

DOC_TOOL_SCHEMA = [
    {
        "name": "read_document",
        "description": "Read the full contents of a document by file path. "
                        "Returns the text with [PAGE N] markers preserved.",
        "input_schema": {
            "type": "object",
            "properties": {
                "file_path": {"type": "string", "description": "Path to the document"}
            },
            "required": ["file_path"],
        },
    }
]

SUBAGENT_SYSTEM_PROMPT = """You are a document analysis subagent. You have no \
memory of any other conversation — you only know what is in this prompt.

Use the read_document tool to read the assigned document, then extract \
findings relevant to the assigned focus area. Preserve page numbers from \
the [PAGE N] markers in the source text.

When finished, respond with ONLY a JSON array (no prose, no markdown fences) \
in this exact structure:
[
  {"content": "<the finding, 1-3 sentences>", "document_name": "<file name>", "page_number": <int>}
]
"""


def _read_document_tool(tool_name: str, tool_input: dict) -> str:
    if tool_name != "read_document":
        return f"Unknown tool: {tool_name}"
    path = Path(tool_input["file_path"])
    if not path.exists():
        return f"ERROR: file not found at {path}"
    return path.read_text()


def run_document_subagent(file_path: str, focus_area: str) -> list[dict]:
    """
    file_path: document to analyse
    focus_area: the specific concern this subagent should extract findings about
    Returns: list of structured findings with content + document metadata.
    """
    task_prompt = (
        f"Document to analyse: {file_path}\n"
        f"Focus area: {focus_area}\n\n"
        "Read the document and extract findings specifically relevant to "
        "the focus area. Include the correct page number for each finding."
    )

    final_text, _ = run_agentic_loop(
        system_prompt=SUBAGENT_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": task_prompt}],
        tools=DOC_TOOL_SCHEMA,
        tool_executor=_read_document_tool,
        label="document-subagent",
    )

    try:
        return json.loads(_strip_fences(final_text))
    except json.JSONDecodeError:
        return [{"content": final_text.strip(), "document_name": file_path, "page_number": None}]


def _strip_fences(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1]
        if text.endswith("```"):
            text = text.rsplit("```", 1)[0]
    return text.strip()
