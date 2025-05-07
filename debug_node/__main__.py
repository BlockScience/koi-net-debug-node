import uvicorn
from .core import node

uvicorn.run(
    "debug_node.server:app", 
    host=node.config.server.host, 
    port=node.config.server.port
)