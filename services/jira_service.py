# services/jira_service.py
from services.base_service import BaseService
from config import JiraConfig

class JiraService(BaseService):
    def __init__(self, base_jira_url=JiraConfig.JIRA_URL, base_marketplace_url=JiraConfig.MARKETPLACE_URL, headers=JiraConfig.HEADERS):
        super().__init__()
        self.jira_url = base_jira_url
        self.marketplace_url = base_marketplace_url
        self.headers = headers

    def _build_url(self, route, use_marketplace=False, use_original_host=False):
        if use_original_host:
            return f"{self.jira_url}/{route}"
        if use_marketplace:
            return f"{self.marketplace_url}/{route}"
        return f"{self.jira_url}/rest/api/2/{route}"

    def create_customer(self, email, name):
        url = self._build_url("rest/servicedeskapi/customer", use_original_host=True)
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
        url = self._build_url(f"rest/api/3/user?accountId={query}&expand=applicationRoles", use_original_host=True)
        return self.get(url, headers=self.headers)

    def get_all_addons(self, route):
        url = self._build_url(route, use_marketplace=True)
        return self.get(url, headers=self.headers)

    def get_addon_detail(self, addon_key):
        url = self._build_url(f"rest/2/addons/{addon_key}", use_marketplace=True)
        return self.get(url, headers=self.headers)
