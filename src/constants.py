from enum import Enum

class RedisChannels(Enum):
    SENTINELS_INPUT = "sentinels:input"
    AGENT_INPUT = "agent:input"
    PERSISTENCE = "system:persistence"

class TransactionStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class AgentDecision(str, Enum):
    APPROVED = "approved"
    REJECTED = "rejected"
    WARNINGS = "warnings"
