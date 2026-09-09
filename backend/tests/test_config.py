from app.core.config import Settings


def test_comma_separated_cors_origins_are_loaded() -> None:
    settings = Settings(cors_origins="http://localhost:3000, http://192.168.1.10:3000")
    assert settings.cors_origins == ["http://localhost:3000", "http://192.168.1.10:3000"]


def test_database_url_is_required_shape() -> None:
    settings = Settings(database_url="postgresql+psycopg://user:pass@localhost/db")
    assert settings.database_url.startswith("postgresql+psycopg://")
