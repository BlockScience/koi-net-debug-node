from dataclasses import dataclass

from slack_bolt import App
from rid_lib import RIDType
from rid_lib.types import KoiNetNode, KoiNetEdge, SlackMessage
from koi_net.protocol import KnowledgeObject
from koi_net.components.interfaces import (
    KnowledgeHandler, 
    HandlerType, 
    STOP_CHAIN
)

from .config import DebugNodeConfig


@dataclass
class DashboardReporter(KnowledgeHandler):
    slack_app: App
    config: DebugNodeConfig
    
    handler_type = HandlerType.RID

    def handle(self, kobj: KnowledgeObject):
        if kobj.source is not None and kobj.event_type is not None:
            
            url = None
            if type(kobj.rid) == SlackMessage:
                url = f"https://blockscienceteam.slack.com/archives/{kobj.rid.channel_id}/p{kobj.rid.ts.replace('.', '')}"
            elif type(kobj.rid) == RIDType.from_string("orn:hackmd.note"):
                url = f"https://hackmd.io/{kobj.rid.reference}"
                
            hyperlink = f" - <{url}|link>" if url else ""
        
            self.slack_app.client.chat_postMessage(
                channel=self.config.debug.slack_channel,
                text=f"`[{kobj.event_type}] {kobj.rid}`{hyperlink}"
            )
            
            if type(kobj.rid) not in (KoiNetNode, KoiNetEdge):
                return STOP_CHAIN