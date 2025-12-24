from agno.db.sqlite import SqliteDb


DATABASE_PATH = "data/incubator.db"
MEMORY_TABLE = "memories"
SESSION_TABLE = "sessions"

DATABASE = SqliteDb(
    db_file=DATABASE_PATH, memory_table=MEMORY_TABLE, session_table=SESSION_TABLE
)
