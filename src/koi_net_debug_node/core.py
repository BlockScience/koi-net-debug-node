import logging
from slack_bolt import App
from koi_net import NodeInterface
from .config import DebugNodeConfig

logger = logging.getLogger(__name__)

node = NodeInterface(
    config=DebugNodeConfig.load_from_yaml("config.yaml"),
    use_kobj_processor_thread=True
)

slack_app = App(
    token=node.config.env.slack_bot_token, 
    signing_secret=node.config.env.slack_signing_secret
)


from . import handlers