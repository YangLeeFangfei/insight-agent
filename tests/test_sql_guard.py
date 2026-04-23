from insight_agent.analysis.sql_guard import validate_read_only_sql


def test_validate_read_only_sql_accepts_select() -> None:
    assert validate_read_only_sql("SELECT * FROM articles") is True


def test_validate_read_only_sql_rejects_delete() -> None:
    assert validate_read_only_sql("DELETE FROM articles") is False
