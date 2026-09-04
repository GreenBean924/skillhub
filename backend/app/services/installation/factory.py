from app.services.installation.adapter import AgentAdapter, AgentType
from app.services.installation.claude_code import ClaudeCodeAdapter

_ADAPTERS: dict[AgentType, type[AgentAdapter]] = {
    AgentType.CLAUDE_CODE: ClaudeCodeAdapter,
}


class AdapterFactory:
    @staticmethod
    def create(agent_type: AgentType) -> AgentAdapter:
        adapter_cls = _ADAPTERS.get(agent_type)
        if adapter_cls is None:
            raise ValueError(f"No adapter registered for agent type: {agent_type}")
        return adapter_cls()
