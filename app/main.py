from fastapi import FastAPI

from app.config import Settings

settings = Settings.from_env()
app = FastAPI(title="AWS CI/CD Demo", version=settings.version)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "healthy"}


@app.get("/api/version")
def version() -> dict[str, str]:
    return {"version": settings.version}


@app.get("/api/config")
def config() -> dict[str, str]:
    return {"environment": settings.environment}
