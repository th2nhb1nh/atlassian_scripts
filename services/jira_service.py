# services/jira_service.py
from services.base_service import BaseService
from config import JiraConfig

class JiraService(BaseService):
    def __init__(self, base_url=JiraConfig.URL, headers=JiraConfig.HEADERS):
        super().__init__()
        self.url = base_url
        self.headers = headers

    def _build_url(self, route, use_original_host=False):
        if use_original_host:
            return f"{self.url}/{route}"
        return f"{self.url}/rest/api/2/{route}"

    def create_customer(self, email, name):
        url = self._build_url("rest/servicedeskapi/customer", True)
        body = {
            "email": email,
            "displayName": name
        }
        return self.post(url, json=body, headers=self.headers)

    def create_user(self, email, name):
        url = self._build_url("user")
        body = {
            "emailAddress": email,
            "name": name,
            "products": [
                "jira-servicedesk"
            ]
        }
        return self.post(url, json=body, headers=self.headers)

    def list_fields(self):
        url = self._build_url("field")
        return self.get(url, headers=self.headers)

    def get_user(self, query):
        url = self._build_url(f"rest/api/3/user?accountId={query}&expand=applicationRoles", True)
        return self.get(url, headers=self.headers)

    def get_all_addons(self, route):
        marketplace_url = "https://marketplace.atlassian.com"
        url = f"{marketplace_url}/{route}"
        print(url)
        return self.get(url, headers=self.headers)
