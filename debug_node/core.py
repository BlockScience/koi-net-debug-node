import logging
from slack_bolt import App
from koi_net import NodeInterface
from koi_net.processor.default_handlers import (
    basic_rid_handler,
    basic_manifest_handler,
    edge_negotiation_handler,
    basic_network_output_filter
)
from .config import DebugNodeConfig

logger = logging.getLogger(__name__)

node = NodeInterface(
    config=DebugNodeConfig.load_from_yaml("config.yaml"),
    use_kobj_processor_thread=True,
    handlers=[
        basic_rid_handler,
        basic_manifest_handler,
        edge_negotiation_handler,
        basic_network_output_filter
    ]
)

slack_app = App(
    token=node.config.env.slack_bot_token, 
    signing_secret=node.config.env.slack_signing_secret
)


from . import handlers