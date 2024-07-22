# base_service.py
import requests

class BaseService:
    def __init__(self, headers=None):
        self.headers = headers or {}

    def _build_url(self, route):
        raise NotImplementedError

    @staticmethod
    def _handle_response(resp, full_resp=False):
        if resp.status_code in [200, 201]:
            return resp if full_resp else resp.json()
        if resp.status_code == 204:
            return True
        print(resp.text)
        return None

    def request(self, url, method="GET", full_resp=False, **kwargs):
        kwargs["headers"] = self.headers
        resp = requests.request(method=method, url=url, **kwargs)
        return self._handle_response(resp, full_resp=full_resp)

    def get(self, url, **kwargs):
        return self.request(url=url, **kwargs)

    def post(self, url, **kwargs):
        return self.request(url=url, method="POST", **kwargs)

    def put(self, url, **kwargs):
        return self.request(url=url, method="PUT", **kwargs)

    def delete(self, url, **kwargs):
        return self.request(url=url, method="DELETE", **kwargs)
