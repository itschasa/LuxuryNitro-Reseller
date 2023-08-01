import httpx
import traceback
import time
import asyncio

from .errors import RetryTimeout, APIError

class HTTP():
    def __init__(self, api_key:str, base_url:str, timeout:int=25, max_retries:int=5, *args) -> None:
        self.api_key = api_key
        self.base_url = base_url
        self.timeout = timeout
        self.max_retries = max_retries
        
        self._http = httpx.AsyncClient(
            cookies  = {'ssid': self.api_key},
            base_url = self.base_url,
            timeout  = self.timeout,
            *args
        )

    async def _exec_retries(self, method, *args, **kwargs) -> httpx.Response:
        errors = []
        for _ in range(self.max_retries):
            try:
                return await method(*args, **kwargs)
            except httpx.HTTPError as e:
                errors.append(e)
        raise RetryTimeout(f"Max retries done: {errors[-1]}", errors)
    
    async def _req(self, method, *args, **kwargs) -> httpx.Response:
        while True:
            res = await self._exec_retries(method, *args, **kwargs)
            if res.status_code == 429:
                await asyncio.sleep(float(res.headers['X-Ratelimit-Reset-After']) + 0.1)
            else:
                try:
                    res.raise_for_status()
                except httpx.HTTPStatusError:
                    try: message = res.json()['message']
                    except: message = res.text
                    if res.status_code >= 500:
                        continue    
                    raise APIError(message, res)
                else:
                    return res

    async def get(self, *args, **kwargs) -> httpx.Response:
        return await self._req(self._http.get, *args, **kwargs)

    async def post(self, *args, **kwargs) -> httpx.Response:
        return await self._req(self._http.post, *args, **kwargs)
    
    async def delete(self, *args, **kwargs) -> httpx.Response:
        return await self._req(self._http.delete, *args, **kwargs)