from sqlalchemy import text

def test_database_connection(mock_db):
    # Mock the chain: mock_db.execute().scalar_one() -> 1
    mock_db.execute.return_value.scalar_one.return_value = 1
    
    result = mock_db.execute(text("SELECT 1")).scalar_one()
    assert result == 1
    mock_db.execute.assert_called_once()