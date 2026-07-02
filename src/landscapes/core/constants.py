import os
from agno.db.sqlite import SqliteDb
from pathlib import Path
from textwrap import dedent

ROOT_DIRECTORY = Path(__file__).parent.parent.parent
NPM_DIRECTORY = os.getenv("NPM_BIN_PATH", os.path.expanduser("~/.npm-global/bin"))
DATABASE_PATH = "data/incubator.db"
MEMORY_TABLE = "memories"
SESSION_TABLE = "sessions"

DATABASE = SqliteDb(
    db_file=DATABASE_PATH, memory_table=MEMORY_TABLE, session_table=SESSION_TABLE
)

DEFAULT_MODEL_NAME = "qwen3:1.7b"
# DEFAULT_MODEL_NAME = "functiongemma"
DEFAULT_INSTRUCTIONS = dedent(
    """
        You are a self-directed agent. Your goal is to autonomously complete tasks using the tools available to you.
        **Tool Usage Instructions**:
        - When you need to look up information on the web, use the `tavily-search` tool.
        - When you want to save or retrieve memories, use the `update_user_memory` tool.
            - After completing a task, always use `update_user_memory` to record what you learned.
            - Remember memories to the degree the information surprises you, is novel, or is otherwise important. Do not remember unimportant details.
        - When you need to access academic papers, use the `arxiv-search` tool.

"""
)

DEFAULT_AGENT_ID = "a_1"
DEFAULT_AGENT_NAME = f"agent_{DEFAULT_AGENT_ID}"
DEFAULT_USER_ID = "u_1"

DEFAULT_COLORS = ["red", "green", "yellow", "bright_yellow", "blue", "magenta", "cyan"]
