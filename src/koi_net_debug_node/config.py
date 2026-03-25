from pydantic import BaseModel, Field
from koi_net.config import (
    FullNodeConfig, 
    KoiNetConfig, 
    FullNodeProfile, 
    EnvConfig
)


class DebugEnvConfig(EnvConfig):
    slack_bot_token: str
    slack_signing_secret: str
    slack_app_token: str
    
class DebugConfig(BaseModel):
    slack_channel: str | None = None

class DebugNodeConfig(FullNodeConfig):
    koi_net: KoiNetConfig = KoiNetConfig(
        node_name="debug",
        node_profile=FullNodeProfile())
    env: DebugEnvConfig = Field(default_factory=DebugEnvConfig)
    debug: DebugConfig = DebugConfig()
