from enum import Enum

class RedisChannels(str, Enum):
    SENTINELS_INPUT = "baiby:sentinels:input"
    SENTINELS_OUTPUT = "baiby:sentinels:output" 

class RequestStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    ERROR = "error"