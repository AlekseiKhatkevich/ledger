from config import settings


def test_set_settings(test_client_no_auth):
    assert test_client_no_auth.app.state.settings == settings
