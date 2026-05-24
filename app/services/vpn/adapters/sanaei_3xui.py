import httpx
from app.services.vpn.adapters.base import VpnPanelAdapter, VpnPanelError


class Sanaei3xUiAdapter(VpnPanelAdapter):
    """Based on official 3x-ui routes: /login and /panel/api/inbounds/*"""

    def __init__(self, base_url: str, username: str, password: str):
        self.base_url = base_url.rstrip("/")
        self.username = username
        self.password = password
        self.client = httpx.AsyncClient(timeout=20)

    async def _login(self):
        r = await self.client.post(f"{self.base_url}/login", data={"username": self.username, "password": self.password})
        if r.status_code != 200:
            raise VpnPanelError("AUTH_FAILED", "احراز هویت پنل ناموفق بود", r.text)

    async def _post(self, path: str, data: dict | None = None):
        await self._login()
        r = await self.client.post(f"{self.base_url}{path}", json=data or {})
        if r.status_code >= 400:
            raise VpnPanelError("API_ERROR", "خطا در ارتباط با پنل", r.text)
        return r.json() if r.text else {"success": True}

    async def _get(self, path: str):
        await self._login()
        r = await self.client.get(f"{self.base_url}{path}")
        if r.status_code >= 400:
            raise VpnPanelError("API_ERROR", "خطا در ارتباط با پنل", r.text)
        return r.json()

    async def test_connection(self): return await self.list_inbounds()
    async def list_inbounds(self): return await self._get("/panel/api/inbounds/list")
    async def create_client(self, payload: dict): return await self._post("/panel/api/inbounds/addClient", payload)
    async def update_client(self, payload: dict): return await self._post(f"/panel/api/inbounds/updateClient/{payload['client_id']}", payload)
    async def renew_client(self, payload: dict): return await self.update_client(payload)
    async def add_traffic(self, payload: dict): return await self.update_client(payload)
    async def reset_traffic(self, payload: dict): return await self._post(f"/panel/api/inbounds/{payload['inbound_id']}/resetClientTraffic/{payload['email']}", payload)
    async def disable_client(self, payload: dict): payload["enable"] = False; return await self.update_client(payload)
    async def enable_client(self, payload: dict): payload["enable"] = True; return await self.update_client(payload)
    async def delete_client(self, payload: dict): return await self._post(f"/panel/api/inbounds/{payload['inbound_id']}/delClient/{payload['client_id']}")
    async def get_client_usage(self, payload: dict): return await self._get(f"/panel/api/inbounds/getClientTraffics/{payload['email']}")
    async def get_config_link(self, payload: dict): return {"link": payload.get("config_link", "")}
    async def get_subscription_link(self, payload: dict): return {"link": payload.get("sub_link", "")}
    async def reset_subscription_link(self, payload: dict): return await self._post("/panel/api/inbounds/resetAllTraffics")
