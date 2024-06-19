import os
import httpx
import dto


class SMSAdapter:
    @staticmethod
    async def send_request(action: str, method: str = 'get', **kwargs):
        async with httpx.AsyncClient(
                headers={'Authorization': f'Basic {os.environ.get("SMS_SERVICE_API_TOKEN")}'},
        ) as client:
            return await client.request(
                url=f"{os.environ.get('SMS_SERVICE_URL')}{action}",
                method=method,
                **kwargs,
            )

    async def send(self, data: dto.SendSmsDto):
        return await self.send_request('/send', 'post', json=data.model_dump(by_alias=True))
