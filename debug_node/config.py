from pydantic import BaseModel, Field
from koi_net.protocol.node import NodeProfile, NodeType, NodeProvides
from koi_net.config import NodeConfig, EnvConfig, KoiNetConfig


class DebugEnvConfig(EnvConfig):
    slack_bot_token: str | None = "SLACK_BOT_TOKEN"
    slack_signing_secret: str | None = "SLACK_SIGNING_SECRET"
    slack_app_token: str | None = "SLACK_APP_TOKEN"
    
class DebugConfig(BaseModel):
    slack_channel: str | None = None

class DebugNodeConfig(NodeConfig):
    koi_net: KoiNetConfig | None = Field(default_factory = lambda: 
        KoiNetConfig(
            node_name="slack-sensor",
            node_profile=NodeProfile(
                node_type=NodeType.FULL,
                provides=NodeProvides()
            )
        )
    )
    env: DebugEnvConfig | None = Field(default_factory=DebugEnvConfig)
    debug: DebugConfig | None = Field(default_factory=DebugConfig)
