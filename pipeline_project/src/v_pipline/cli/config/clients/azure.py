import requests

from v_pipline.cli.config.config import Config


class AzureGraphClient:
	def __init__(self, tenent_id: str, client_id: str, client_secret: str, resource_url: str):
		self.tenent_id = tenent_id
		self.client_id = client_id
		self.client_secret = client_secret
		self.resource_url = resource_url
		self.base_url = f"https://login.microsoftonline.com/{self.tenent_id}/oauth2/v2.0/token"
		self.headers = {
			"Content-Type": "application/x-www-form-urlencoded",
		}

	@property
	def auth_headers(self):
		access_token = self.get_access_token()
		return {"Authorization": f"Bearer {access_token}"}

	def get_access_token(self):
		data = {
			"grant_type": "client_credentials",
			"client_id": self.client_id,
			"client_secret": self.client_secret,
			"scope": self.resource_url + "/.default",
		}
		response = requests.post(self.base_url, headers=self.headers, data=data)
		response.raise_for_status()
		return response.json()["access_token"]

	def get_site_id(self, site_url: str):
		full_url = f"{self.resource_url}/sites/{site_url}"
		headers = self.auth_headers
		response = requests.get(full_url, headers=headers)
		response.raise_for_status()
		return response.json()["id"]

	def get_drives(self, site_url: str):
		site_id = self.get_site_id(site_url)
		full_url = f"{self.resource_url}/sites/{site_id}/drives"
		headers = self.auth_headers
		response = requests.get(full_url, headers=headers)
		response.raise_for_status()
		return response.json().get("value", [])

	def get_drive_id(self, site_url: str):
		drives = self.get_drives(site_url)
		return [(drive.get("id"), drive.get("name")) for drive in drives]

	@staticmethod
	def from_config(config: Config):
		sharepoint = config.get_provider("azure")
		return AzureGraphClient(
			tenent_id=sharepoint.get("tenent_id"),
			client_id=sharepoint.get("client_id"),
			client_secret=sharepoint.get("client_secret"),
			resource_url=sharepoint.get("resource_url"),
		)


if __name__ == "__main__":
	config = Config.from_config_file("vp")
	client = AzureGraphClient.from_config(config)
	access_token = client.get_access_token()
	print(access_token)
