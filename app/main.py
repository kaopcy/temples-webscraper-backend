import logging
import logging.config
from os import path
from typing import Union

from fastapi import FastAPI, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

from app.configs.config import initialDatabase
# middlewares
from app.middlewares.requestValidationException import http_exception_handler
from app.routes.image import router as ImageRoute
from app.routes.province import router as ProvinceRoute
from app.routes.temple import router as TempleRouter
from app.routes.test import router as TestRoute
from app.services.cron import scraping_temples

app = FastAPI()

log_file_path = path.join(path.dirname(path.abspath(__file__)), 'logging.conf')
logging.basicConfig(filename='log.txt',
                    filemode='a',
                    format='%(asctime)s %(name)20s %(levelname)8s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.DEBUG)
logger = logging.getLogger(__name__)


@app.on_event('startup')
async def start_database():
    logger.info('started')
    await initialDatabase()
    print('started')
    app.add_middleware(
        CORSMiddleware,
        allow_origins=['*'],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    # app.add_exception_handler(RequestValidationError, http_exception_handler)
    app.include_router(TempleRouter, tags=["Temple"], prefix="/temple")
    app.include_router(ProvinceRoute, tags=["Province"], prefix="/province")
    app.include_router(TestRoute, tags=["Province"], prefix="/test")
    app.include_router(ImageRoute, tags=["Image"], prefix="/image")
    app.add_event_handler('startup', scraping_temples)


@app.get("/", tags=['Root'])
def read_root():
    return {"server": "running!"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}
