
from fastapi import Request

from fastapi.encoders import jsonable_encoder

async def json_response_middleware(request: Request , call_next):
    response = await call_next(request)
    if "application/json" in response.headers.getlist('content-type'):
        response.body = jsonable_encoder(response.body)
    return response

