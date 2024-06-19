import json
import os

import fastapi
from starlette import status
import dto
from adapters import SMSAdapter
import httpx
from fastapi.middleware.cors import CORSMiddleware

app = fastapi.FastAPI() 

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


@app.post('/sms/send/{id_}')
async def send_sms(id_: int):
    response = httpx.get(f'{os.environ.get("CORE_URL")}/api/user/{id_}')

    try:
        as_json = response.json()

        data = {'from': 'Info', 'to': str(as_json.get("phone")), 'text': str(as_json.get('code'))}
        body = dto.SendSmsDto(**data)

        await SMSAdapter().send(body)
    except json.JSONDecodeError as e:
        print('JSON Decode Error:', e)

    return fastapi.responses.Response(status_code=status.HTTP_204_NO_CONTENT)


if __name__ == '__main__':
    import uvicorn

    uvicorn.run('main:app', host='0.0.0.0', port=1026)
