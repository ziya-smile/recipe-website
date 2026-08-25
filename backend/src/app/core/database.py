import os
from pathlib import Path
from threading import Lock

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

_lock = Lock()
_engine = None
_SessionLocal = None

Base = declarative_base()


def data_dir() -> Path:
    if os.environ.get("VERCEL"):
        return Path("/tmp/recipe_data")
    return Path(os.environ.get("RECIPE_DATA_DIR", Path(__file__).resolve().parent.parent.parent.parent / "data"))


def uploads_dir() -> Path:
    path = data_dir() / "uploads"
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_db_url() -> str:
    url = (
        os.environ.get("DATABASE_URL")
        or os.environ.get("POSTGRES_URL")
        or os.environ.get("POSTGRES_PRISMA_URL")
    )
    if url:
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql://", 1)
        return url

    db_dir = data_dir()
    db_dir.mkdir(parents=True, exist_ok=True)
    db_file = db_dir / "recipes.db"
    return f"sqlite:///{db_file}"


def is_postgres() -> bool:
    return get_db_url().startswith("postgresql")


def get_db_type() -> str:
    return "PostgreSQL (Cloud)" if is_postgres() else "SQLite (Local)"


def get_session_factory(seed_func=None):
    global _engine, _SessionLocal
    if _SessionLocal is None:
        db_url = get_db_url()
        connect_args = {}
        engine_kwargs = {"pool_pre_ping": True}
        if db_url.startswith("sqlite"):
            connect_args["check_same_thread"] = False
            engine_kwargs.pop("pool_pre_ping", None)

        _engine = create_engine(db_url, connect_args=connect_args, **engine_kwargs)
        Base.metadata.create_all(bind=_engine)
        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_engine)

        if seed_func:
            seed_func(_SessionLocal)

    return _SessionLocal


def reset() -> None:
    global _engine, _SessionLocal
    with _lock:
        if _engine is not None:
            _engine.dispose()
        _engine = None
        _SessionLocal = None
        db_file = data_dir() / "recipes.db"
        if db_file.exists():
            db_file.unlink()
