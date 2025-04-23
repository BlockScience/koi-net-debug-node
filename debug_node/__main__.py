import uvicorn
from .config import HOST, PORT

uvicorn.run("debug_node.server:app", host=HOST, port=PORT)