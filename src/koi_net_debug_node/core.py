from slack_bolt import App
from koi_net.core import FullNode
from koi_net.processor.knowledge_handlers import (
    basic_manifest_handler, 
    basic_network_output_filter, 
    basic_rid_handler, 
    edge_negotiation_handler, 
    forget_edge_on_node_deletion, 
    secure_profile_handler
)

from .config import DebugNodeConfig
from .handlers import ExtendedHandlerContext, dashboard_reporter, greedy_contact_handler


class DebugNode(FullNode):
    config_schema = DebugNodeConfig
    slack_app = lambda config: App(
        token=config.env.slack_bot_token, 
        signing_secret=config.env.slack_signing_secret
    )
    handler_context = ExtendedHandlerContext
    knowledge_handlers = [
        # default handlers
        basic_manifest_handler, 
        basic_network_output_filter, 
        basic_rid_handler, 
        edge_negotiation_handler, 
        forget_edge_on_node_deletion, 
        secure_profile_handler,
        # replacing node contact 
        greedy_contact_handler,
        # custom handler
        dashboard_reporter
    ]
