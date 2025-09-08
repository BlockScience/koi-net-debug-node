from koi_net.protocol.edge import generate_edge_bundle
from rid_lib import RIDType
from rid_lib.types import KoiNetNode, KoiNetEdge, SlackMessage
from koi_net.context import HandlerContext
from koi_net.protocol.edge import EdgeType
from koi_net.processor.handler import HandlerType, STOP_CHAIN
from koi_net.processor.knowledge_object import KnowledgeObject
from koi_net.protocol.node import NodeProfile
from .core import slack_app, node



@node.pipeline.register_handler(HandlerType.RID)
def dashboard_reporter(ctx, kobj: KnowledgeObject):
    if kobj.source is not None and kobj.event_type is not None:
        
        url = None
        if type(kobj.rid) == SlackMessage:
            url = f"https://blockscienceteam.slack.com/archives/{kobj.rid.channel_id}/p{kobj.rid.ts.replace('.', '')}"
        elif type(kobj.rid) == RIDType.from_string("orn:hackmd.note"):
            url = f"https://hackmd.io/{kobj.rid.reference}"
            
        hyperlink = f" - <{url}|link>" if url else ""
    
        slack_app.client.chat_postMessage(
            channel=node.config.debug.slack_channel,
            text=f"`[{kobj.event_type}] {kobj.rid}`{hyperlink}"
        )
        
        if type(kobj.rid) not in (KoiNetNode, KoiNetEdge):
            return STOP_CHAIN
    
@node.pipeline.register_handler(HandlerType.Network, rid_types=[KoiNetNode])
def greedy_contact(ctx: HandlerContext, kobj: KnowledgeObject):
    # when I found out about a new node
    
    if kobj.rid == ctx.identity.rid:
        return
    
    node_profile = kobj.bundle.validate_contents(NodeProfile)
    
    if ctx.graph.get_edge(
        source=kobj.rid,
        target=ctx.identity.rid,
    ) is not None:
        return
    
    if not node_profile.provides.event:
        return
    
    # queued for processing
    ctx.handle(bundle=generate_edge_bundle(
        source=kobj.rid,
        target=ctx.identity.rid,
        edge_type=EdgeType.WEBHOOK,
        # subscribes to all events for provided RID types
        rid_types=node_profile.provides.event
    ))
