import httpx
import qrcode
from io import BytesIO
from app.services.vpn.adapters.base import VpnPanelAdapter


class SanaeiApiError(Exception):
    pass


class Sanaei3xUiAdapter(VpnPanelAdapter):
    def __init__(self, host: str, port: int, username: str, password: str, base_path: str = ""):
        self.base = f"http://{host}:{port}{base_path}".rstrip("/")
        self.username = username
        self.password = password
        self.client = httpx.AsyncClient(timeout=20.0)

    async def _login(self):
        r = await self.client.post(f"{self.base}/login", json={"username": self.username, "password": self.password})
        if r.status_code >= 400:
            raise SanaeiApiError("خطا در احراز هویت پنل 3x-ui")

    async def _req(self, method: str, path: str, **kwargs):
        await self._login()
        r = await self.client.request(method, f"{self.base}/panel/api/inbounds{path}", **kwargs)
        if r.status_code >= 400:
            raise SanaeiApiError(f"خطا در ارتباط با API پنل: {r.status_code}")
        data = r.json() if r.text else {}
        if isinstance(data, dict) and data.get("success") is False:
            raise SanaeiApiError(data.get("msg") or "خطای نامشخص پنل")
        return data

    async def test_connection(self): return await self.list_inbounds()
    async def list_inbounds(self): return await self._req("GET", "/list")
    async def create_client(self, inbound_id: int, client: dict): return await self._req("POST", "/addClient", json={"id": inbound_id, "settings": '{"clients":[' + str(client).replace("'", '"') + ']}'})
    async def update_client(self, client_id: str, payload: dict): return await self._req("POST", f"/updateClient/{client_id}", json=payload)
    async def renew_client(self, client_id: str, expiry_time_ms: int): return await self.update_client(client_id, {"expiryTime": expiry_time_ms})
    async def add_traffic(self, client_id: str, bytes_amount: int): return await self.update_client(client_id, {"totalGB": bytes_amount})
    async def reset_traffic(self, email: str): return await self._req("POST", f"/resetClientTraffic/{email}")
    async def disable_client(self, client_id: str): return await self.update_client(client_id, {"enable": False})
    async def enable_client(self, client_id: str): return await self.update_client(client_id, {"enable": True})
    async def delete_client(self, inbound_id: int, client_id: str): return await self._req("POST", f"/{inbound_id}/delClient/{client_id}")
    async def get_client_usage(self, email: str): return await self._req("GET", f"/getClientTraffics/{email}")
    async def get_config_link(self, inbound_id: int, email: str): return f"{self.base}/panel/inbounds/{inbound_id}/client/{email}"
    async def get_subscription_link(self, sub_id: str): return f"{self.base}/sub/{sub_id}"
    async def reset_subscription_link(self, inbound_id: int, email: str): return await self._req("POST", f"/resetClientIp/{email}")

    @staticmethod
    def qrcode_png_bytes(link: str) -> bytes:
        img = qrcode.make(link)
        buf = BytesIO()
        img.save(buf, format="PNG")
        return buf.getvalue()
