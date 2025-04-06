from enum import Enum

class RedisChannels(str, Enum):
    SENTINELS_INPUT = "baiby:sentinels:input"
    # SENTINELS_OUTPUT = "baiby:sentinels:output" 
    AGENT_INPUT = "baiby:agent:input"
    # AGENT_OUTPUT = "baiby:agent:output"

class RequestStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    ERROR = "error"

class AgentDecision(str, Enum):
    APPROVED = "approved"
    REJECTED = "rejected"
    WARNINGS = "warnings"
