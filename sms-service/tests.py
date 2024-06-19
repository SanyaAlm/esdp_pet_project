from unittest.mock import AsyncMock, patch
import os
from main import app
from fastapi.testclient import TestClient
import pytest
from dto import SendSmsDto
from starlette import status


client = TestClient(app)


@pytest.mark.asyncio
async def test_send_sms(mocker):
    mock_httpx_get = mocker.patch('httpx.get')
    mock_response = mocker.Mock()
    mock_response.json.return_value = {'phone': '123456789', 'code': '1234'}
    mock_httpx_get.return_value = mock_response

    with patch('adapters.SMSAdapter.send', new_callable=AsyncMock) as mock_sms_adapter_send:
        response = client.post('/sms/send/1')
        test = {'from': 'Info', 'to': mock_response.json.return_value['phone'], 'text': mock_response.json.return_value['code']}
        mock_httpx_get.assert_called_once_with(f'{os.environ.get("CORE_URL")}/api/user/1')
        mock_sms_adapter_send.assert_called_once_with(SendSmsDto(**test))

        assert response.status_code == status.HTTP_204_NO_CONTENT
