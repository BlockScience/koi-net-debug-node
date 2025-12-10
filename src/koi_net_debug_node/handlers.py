from dataclasses import dataclass

import structlog
from slack_bolt import App
from rid_lib import RIDType
from rid_lib.ext import Bundle
from rid_lib.types import KoiNetNode, KoiNetEdge, SlackMessage
from koi_net.protocol.edge import generate_edge_bundle
from koi_net.protocol.edge import EdgeType
from koi_net.protocol.node import NodeProfile
from koi_net.processor.handler import (
    KnowledgeHandler, 
    HandlerType, 
    HandlerContext,
    KnowledgeObject,
    STOP_CHAIN
)
from koi_net.protocol.edge import EdgeProfile, EdgeStatus, EdgeType, generate_edge_bundle
from koi_net.protocol.node import NodeType
from koi_net.processor.handler import HandlerContext

from .config import DebugNodeConfig

log = structlog.stdlib.get_logger()


@dataclass
class ExtendedHandlerContext(HandlerContext):
    config: DebugNodeConfig
    slack_app: App

@KnowledgeHandler.create(HandlerType.RID)
def dashboard_reporter(ctx: ExtendedHandlerContext, kobj: KnowledgeObject):
    if kobj.source is not None and kobj.event_type is not None:
        
        url = None
        if type(kobj.rid) == SlackMessage:
            url = f"https://blockscienceteam.slack.com/archives/{kobj.rid.channel_id}/p{kobj.rid.ts.replace('.', '')}"
        elif type(kobj.rid) == RIDType.from_string("orn:hackmd.note"):
            url = f"https://hackmd.io/{kobj.rid.reference}"
            
        hyperlink = f" - <{url}|link>" if url else ""
    
        ctx.slack_app.client.chat_postMessage(
            channel=ctx.config.debug.slack_channel,
            text=f"`[{kobj.event_type}] {kobj.rid}`{hyperlink}"
        )
        
        if type(kobj.rid) not in (KoiNetNode, KoiNetEdge):
            return STOP_CHAIN
    
@KnowledgeHandler.create(HandlerType.Network, rid_types=[KoiNetNode])
def greedy_contact_handler(ctx: HandlerContext, kobj: KnowledgeObject):
    """Makes contact with providers of any RID type.
    
    Copies functionality of built in node contact handler, but acts as
    if all RID types are of interest.
    """
    # prevents nodes from attempting to form a self loop
    if kobj.rid == ctx.identity.rid:
        return
    
    node_profile = kobj.bundle.validate_contents(NodeProfile)
    
    available_rid_types = node_profile.provides.event
    
    if not available_rid_types:
        return
    
    edge_rid = ctx.graph.get_edge(
        source=kobj.rid,
        target=ctx.identity.rid,
    )
    
    # already have an edge established
    if edge_rid:
        prev_edge_bundle = ctx.cache.read(edge_rid)
        edge_profile = prev_edge_bundle.validate_contents(EdgeProfile)
        
        if set(edge_profile.rid_types) == set(available_rid_types):
            # no change in rid types
            return
        
        log.info(f"Proposing updated edge with node provider {available_rid_types}")
        
        edge_profile.rid_types = available_rid_types
        edge_profile.status = EdgeStatus.PROPOSED
        edge_bundle = Bundle.generate(edge_rid, edge_profile.model_dump())
    
    # no existing edge
    else:
        log.info(f"Proposing new edge with node provider {available_rid_types}")
        edge_bundle = generate_edge_bundle(
            source=kobj.rid,
            target=ctx.identity.rid,
            rid_types=available_rid_types,
            edge_type=(
                EdgeType.WEBHOOK
                if ctx.identity.profile.node_type == NodeType.FULL
                else EdgeType.POLL
            )
        )
    
    # queued for processing
    ctx.kobj_queue.push(bundle=edge_bundle)
    
    log.info("Catching up on network state")
    payload = ctx.request_handler.fetch_rids(
        node=kobj.rid, 
        rid_types=available_rid_types
    )
    for rid in payload.rids:
        if rid == ctx.identity.rid:
            log.info("Skipping myself")
            continue
        if ctx.cache.exists(rid):
            log.info(f"Skipping known RID {rid!r}")
            continue
        
        # marked as external since we are handling RIDs from another node
        # will fetch remotely instead of checking local cache
        ctx.kobj_queue.push(rid=rid, source=kobj.rid)
    log.info("Done")
