#!/usr/bin/env python3
import os

from pydantic import ValidationError
from sanic import Sanic, Request, HTTPResponse, response

from src import db_api
from src.validators import LinkValidator


app = Sanic(__name__)


@app.post('/get_short_link')
async def get_short_link(request: Request) -> HTTPResponse:
    try:
        link = LinkValidator(link=request.body)
    except ValidationError as e:
        return response.json(e.json(), status=400, indent=4)

    status = 200
    if (short_link := db_api.find_short_link(long_link=link.link)) is None:
        short_link = db_api.short_link(long_link=link.link)
        status = 201

    return response.json(short_link.json(), status=status, indent=4)


@app.delete('/delete_link/<link_id:int>')
async def delete_link(request: Request,
                      link_id: int) -> HTTPResponse:
    if (link := db_api.get_link(link_id=link_id)) is None:
        return HTTPResponse(status=404)

    db_api.delete_link(link_id=link_id)
    return response.json(link.json(), status=202)


if __name__ == "__main__":
    app.run(
        port=8081,
        workers=os.cpu_count(),
        access_log=False
    )
