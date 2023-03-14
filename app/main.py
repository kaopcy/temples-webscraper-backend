from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError

from typing import Union
from fastapi import FastAPI, status

from app.configs.config import initialDatabase

# middlewares
from app.middlewares.requestValidationException import http_exception_handler

from app.routes.temple import router as TempleRouter

app = FastAPI()

app.add_exception_handler(RequestValidationError, http_exception_handler)

app.include_router(TempleRouter, tags=["Temple"], prefix="/temple")

@app.on_event('startup')
async def start_database():
    await initialDatabase()

@app.exception_handler(RequestValidationError)
async def http_exception_handler(request, exc: RequestValidationError):
    errMsg = []
    for error in exc.errors():
        # loc means locations
        loc, msg, bodyKeys = error["loc"], error["msg"], list(exc.body.keys())
        print(loc[0] in ("body", "query", "path"))
        filteredLoc = loc[1:] if loc[0] in ("body", "query", "path") else loc
        field = [a for a in filteredLoc if a not in bodyKeys]
        errMsg.append({msg: field})
    return JSONResponse(jsonable_encoder({"detail": exc.errors(), 'errors': errMsg, "body": exc.body}), status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)


@app.get("/", tags=['Root'])
def read_root():
    return {"server": "running!"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}