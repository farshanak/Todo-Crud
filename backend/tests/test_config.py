from config import Settings


def test_defaults_when_env_unset(monkeypatch) -> None:
    for var in ("HOST", "PORT", "CORS_ORIGINS", "LOG_LEVEL"):
        monkeypatch.delenv(var, raising=False)
    s = Settings(_env_file=None)
    assert s.host == "127.0.0.1"
    assert s.port == 8000
    assert s.cors_origins == "http://localhost:5173"
    assert s.log_level == "info"


def test_cors_origins_list_splits_and_strips(monkeypatch) -> None:
    monkeypatch.setenv("CORS_ORIGINS", "http://a.com, http://b.com ,http://c.com")
    s = Settings(_env_file=None)
    assert s.cors_origins_list == [
        "http://a.com",
        "http://b.com",
        "http://c.com",
    ]


def test_cors_origins_list_ignores_blanks(monkeypatch) -> None:
    monkeypatch.setenv("CORS_ORIGINS", "http://a.com,,  ,http://b.com")
    s = Settings(_env_file=None)
    assert s.cors_origins_list == ["http://a.com", "http://b.com"]


def test_port_parsed_as_int(monkeypatch) -> None:
    monkeypatch.setenv("PORT", "9000")
    s = Settings(_env_file=None)
    assert s.port == 9000
    assert isinstance(s.port, int)
