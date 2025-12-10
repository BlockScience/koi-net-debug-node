from pydantic import BaseModel
from koi_net.config.full_node import (
    FullNodeConfig, 
    KoiNetConfig, 
    NodeProfile, 
)
from koi_net.config.core import EnvConfig


class DebugEnvConfig(EnvConfig):
    slack_bot_token: str = "SLACK_BOT_TOKEN"
    slack_signing_secret: str = "SLACK_SIGNING_SECRET"
    slack_app_token: str = "SLACK_APP_TOKEN"
    
class DebugConfig(BaseModel):
    slack_channel: str | None = None

class DebugNodeConfig(FullNodeConfig):
    koi_net: KoiNetConfig = KoiNetConfig(
        node_name="debug",
        node_profile=NodeProfile())
    env: DebugEnvConfig = DebugEnvConfig()
    debug: DebugConfig = DebugConfig()
