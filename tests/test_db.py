def test_database_connection(db_session):
    result = db_session.execute("SELECT 1").scalar()
    assert result == 1