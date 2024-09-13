from typing import Optional

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine


class AsyncSQLDataBase:
	def __init__(self, connection_string: str) -> None:
		self.connection_string = connection_string
		self.engine = None
		self.session = None

	async def connect(self, **engine_kwargs):
		self.engine = create_async_engine(self.connection_string, **engine_kwargs)
		self.session = AsyncSession(self.engine)

	async def disconnect(self):
		if self.session:
			await self.session.close()
		if self.engine:
			await self.engine.dispose()
		self.session = None
		self.engine = None

	async def get_session(self) -> Optional[AsyncSession]:
		return self.session

	async def get_engine(self) -> Optional[AsyncEngine]:
		return self.engine

	async def __aenter__(self):
		return self

	async def __aexit__(self, exc_type, exc, tb):
		await self.disconnect()
		return False
