from config import settings

def test_set_settings(test_client):
    assert test_client.app.state.settings == settings