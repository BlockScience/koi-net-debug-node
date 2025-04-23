from koi_net.protocol.helpers import generate_edge_bundle
from rid_lib import RIDType
from rid_lib.types import KoiNetNode, KoiNetEdge, SlackMessage
from koi_net.processor.interface import ProcessorInterface
from koi_net.protocol.event import EventType
from koi_net.protocol.edge import EdgeType
from koi_net.processor.handler import HandlerType, STOP_CHAIN
from koi_net.processor.knowledge_object import KnowledgeObject, KnowledgeSource
from koi_net.protocol.node import NodeProfile
from .core import slack_app, node



@node.processor.register_handler(HandlerType.RID)
def dashboard(processor: ProcessorInterface, kobj: KnowledgeObject):
    if kobj.source == KnowledgeSource.External and kobj.event_type is not None:
        
        url = None
        if type(kobj.rid) == SlackMessage:
            url = f"https://blockscienceteam.slack.com/archives/{kobj.rid.channel_id}/p{kobj.rid.ts.replace('.', '')}"
        elif type(kobj.rid) == RIDType.from_string("orn:hackmd.note"):
            url = f"https://hackmd.io/{kobj.rid.reference}"
            
        hyperlink = f" - <{url}|link>" if url else ""
    
        slack_app.client.chat_postMessage(
            channel="C088UBMRXC5",
            text=f"`[{kobj.event_type}] {kobj.rid}`{hyperlink}"
        )
        
        if type(kobj.rid) not in (KoiNetNode, KoiNetEdge):
            return STOP_CHAIN
    
@node.processor.register_handler(HandlerType.Network, rid_types=[KoiNetNode])
def coordinator_contact(processor: ProcessorInterface, kobj: KnowledgeObject):
    # when I found out about a new node
    if kobj.normalized_event_type != EventType.NEW: 
        return
    
    if kobj.rid == processor.identity.rid:
        return
    
    node_profile = kobj.bundle.validate_contents(NodeProfile)
    
    # queued for processing
    processor.handle(bundle=generate_edge_bundle(
        source=kobj.rid,
        target=processor.identity.rid,
        edge_type=EdgeType.WEBHOOK,
        rid_types=node_profile.provides.event
    ))
    
    # looking for event provider of nodes
    if KoiNetNode not in node_profile.provides.event:
        return
    
    payload = processor.network.request_handler.fetch_rids(kobj.rid, rid_types=[KoiNetNode])
    for rid in payload.rids:
        if rid == processor.identity.rid:
            continue
        if processor.cache.exists(rid):
            continue
        
        # marked as external since we are handling RIDs from another node
        # will fetch remotely instead of checking local cache
        processor.handle(rid=rid, source=KnowledgeSource.External)
