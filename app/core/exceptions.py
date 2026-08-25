from fastapi import HTTPException


def bad_request(message: str):
    return HTTPException(status_code=400, detail=message)


def unauthorized(message: str):
    return HTTPException(status_code=401, detail=message)


def forbidden(message: str):
    return HTTPException(status_code=403, detail=message)


def not_found(message: str):
    return HTTPException(status_code=404, detail=message)


def method_not_allowed(message: str):
    return HTTPException(status_code=405, detail=message)


def conflict(message: str):
    return HTTPException(status_code=409, detail=message)


def unprocessable_entity(message: str):
    return HTTPException(status_code=422, detail=message)


def internal_server_error(message: str):
    return HTTPException(status_code=500, detail=message)
