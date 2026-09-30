import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    version: str
    environment: str

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            version=os.getenv("APP_VERSION", "dev"),
            environment=os.getenv("APP_ENV", "local"),
        )
