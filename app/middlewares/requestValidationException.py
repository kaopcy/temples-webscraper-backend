
from fastapi import status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

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
