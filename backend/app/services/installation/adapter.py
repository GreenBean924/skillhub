from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path


class AgentType(str, Enum):
    CLAUDE_CODE = "claude_code"


@dataclass
class EnvironmentInfo:
    agent_type: AgentType
    detected: bool
    install_dir: Path | None = None
    version: str | None = None


@dataclass
class InstallationResult:
    success: bool
    slug: str
    agent_type: AgentType
    install_dir: Path | None = None
    message: str = ""
    error: str | None = None


class AgentAdapter(ABC):
    @abstractmethod
    async def detect_environment(self) -> EnvironmentInfo: ...

    @abstractmethod
    async def install_skill(self, slug: str, skill_md: str) -> InstallationResult: ...

    @abstractmethod
    async def uninstall_skill(self, slug: str) -> bool: ...

    @abstractmethod
    async def list_skills(self) -> list[str]: ...

    @abstractmethod
    async def verify_installation(self, slug: str) -> bool: ...
