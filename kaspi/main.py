import os

import fastapi

from xml_generate import generate_xml
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
import httpx
app = fastapi.FastAPI()

origins = ['http://localhost']
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


@app.get('/{partner_id}/kaspi_xml')
async def generate_xml_endpoint(partner_id: int):

    response = httpx.get(f'http://django-app:8000/api/{partner_id}/kaspi_xml')
    as_json = response.json()
    xml_data = await generate_xml(as_json)

    return Response(xml_data, media_type='application/xml')

if __name__ == '__main__':
    import uvicorn

    uvicorn.run('main:app', host='0.0.0.0', port=5050, reload=True)
