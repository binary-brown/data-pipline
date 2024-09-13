import os
from enum import Enum
from typing import Union

from langchain.text_splitter import RecursiveCharacterTextSplitter
from llama_index.core import Document, SimpleDirectoryReader
from llama_index.core.node_parser import (
	LangchainNodeParser,
	SentenceSplitter,
	TokenTextSplitter,
)
from llama_index.vector_stores.postgres import PGVectorStore
from sqlalchemy import make_url


class ChunkType(str, Enum):
	SENTENCE = "sentance"
	TOKEN_COUNT = "token_count"
	SEMANTIC = "semantic"


async def chunk_directory(path_to_data: str, type: ChunkType, chunk_size: int = 1024):
	nodes = []
	documents = SimpleDirectoryReader(path_to_data).load_data()
	node_parser: Union[
		LangchainNodeParser,
		SentenceSplitter,
		TokenTextSplitter,
		RecursiveCharacterTextSplitter,
	]
	match type:
		case ChunkType.SENTENCE:
			node_parser = SentenceSplitter(chunk_size=chunk_size, chunk_overlap=20)
		case ChunkType.TOKEN_COUNT:
			node_parser = TokenTextSplitter(chunk_size=chunk_size, chunk_overlap=20)
		case ChunkType.SEMANTIC:
			node_parser = LangchainNodeParser(RecursiveCharacterTextSplitter())
		case _:
			node_parser = SentenceSplitter(chunk_size=chunk_size, chunk_overlap=20)
	nodes = await node_parser.aget_nodes_from_documents(documents)
	return nodes


async def chunk_file(file_path: str, type: ChunkType, chunk_size: int = 1024):
	with open(file_path, "r") as file:
		text = file.read()
	document = Document(text=text)
	node_parser: Union[
		LangchainNodeParser,
		SentenceSplitter,
		TokenTextSplitter,
		RecursiveCharacterTextSplitter,
	]
	match type:
		case ChunkType.SENTENCE:
			node_parser = SentenceSplitter(chunk_size=chunk_size, chunk_overlap=20)
		case ChunkType.TOKEN_COUNT:
			node_parser = TokenTextSplitter(chunk_size=chunk_size, chunk_overlap=20)
		case ChunkType.SEMANTIC:
			node_parser = LangchainNodeParser(RecursiveCharacterTextSplitter())
		case _:
			node_parser = SentenceSplitter(chunk_size=chunk_size, chunk_overlap=20)
	nodes = await node_parser.aget_nodes_from_documents(documents=[document])
	return nodes


async def vectorize_file(
	path_to_data: str,
	chunk: bool = False,
	type: ChunkType = ChunkType.SENTENCE,
	chunk_size: int = None,
):
	if chunk:
		nodes = await chunk_file(path_to_data, type, chunk_size)
	else:
		pass
	connection_string = os.getenv("DATABASE_URI")
	if connection_string is not None:
		url = make_url(connection_string)
		vector_store = PGVectorStore(
			connection_string=url,
			async_connection_string=url,
			table_name="documents",
			schema_name="public",
		)
	return nodes


async def vectorize_dir(
	path_to_data: str,
	chunk: bool = False,
	type: ChunkType = ChunkType.SENTENCE,
	chunk_size: int = None,
):
	root, _, files = next(os.walk(path_to_data))
	files = []
	for file in files:
		if chunk:
			nodes = await vectorize_file(root + file, chunk, type, chunk_size)
			files.append(nodes)
		else:
			pass
	return files
