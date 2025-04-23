import logging
from slack_bolt import App
from koi_net import NodeInterface
from koi_net.protocol.node import NodeProfile, NodeType, NodeProvides
from .config import URL, SLACK_BOT_TOKEN, SLACK_SIGNING_SECRET, FIRST_CONTACT

logger = logging.getLogger(__name__)

slack_app = App(token=SLACK_BOT_TOKEN, signing_secret=SLACK_SIGNING_SECRET)

node = NodeInterface(
    name="debug",
    profile=NodeProfile(
        base_url=URL,
        node_type=NodeType.FULL,
        provides=NodeProvides()
    ),
    use_kobj_processor_thread=True,
    first_contact=FIRST_CONTACT
)

from . import handlers