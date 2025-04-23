import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, APIRouter
from koi_net.processor.knowledge_object import KnowledgeSource
from koi_net.protocol.api_models import EventsPayload
from koi_net.protocol.consts import BROADCAST_EVENTS_PATH
from .core import node


logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):    
    node.start()
    yield
    node.stop()

app = FastAPI(lifespan=lifespan)

koi_net_router = APIRouter(
    prefix="/koi-net"
)

@koi_net_router.post(BROADCAST_EVENTS_PATH)
def broadcast_events(req: EventsPayload):
    logger.info(f"Request to {BROADCAST_EVENTS_PATH}, received {len(req.events)} event(s)")
    for event in req.events:
        node.processor.handle(event=event, source=KnowledgeSource.External)
    

app.include_router(koi_net_router)