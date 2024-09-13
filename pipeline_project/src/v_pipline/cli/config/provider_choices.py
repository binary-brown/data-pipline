from enum import Enum


class ProviderChoice(str, Enum):
	GOOGLE = "google"
	GITHUB = "github"
	MICROSOFT = "microsoft"
	APPLE = "apple"
