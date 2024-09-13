from enum import Enum


class VPErrorCodes(int, Enum):
	FILE_NOT_FOUND = 0x404
	USER_DECLINED = 0x405
	ALREADY_EXISTS = 0x406
	INVALID_INPUT = 0x407
