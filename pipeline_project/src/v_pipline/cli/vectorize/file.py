import os
from enum import Enum

from langchain.text_splitter import RecursiveCharacterTextSplitter
from llama_index.core import Document, VectorStoreIndex
from llama_index.core.node_parser import (
    LangchainNodeParser,
    SentenceSplitter,
    TokenTextSplitter,
)
from llama_index.vector_stores.postgres import PGVectorStore


class ChunkType(str, Enum):
    SENTENCE = "sentance"
    TOKEN_COUNT = "token_count"
    SEMANTIC = "semantic"


async def chunk_file(path_to_data: str, type: ChunkType, chunk_size: int = 1024):
    nodes = []
    match type:
        case ChunkType.SENTENCE:
            node_parser = SentenceSplitter(chunk_size=chunk_size, chunk_overlap=20)
            nodes = node_parser.get_nodes_from_documents(
                [Document.from_file(path_to_data, show_progress=True)]
            )
        case ChunkType.TOKEN_COUNT:
            node_parser = TokenTextSplitter(chunk_size=chunk_size, chunk_overlap=20)
            nodes = node_parser.get_nodes_from_documents(
                [Document.from_file(path_to_data, show_progress=True)]
            )
        case ChunkType.SEMANTIC:
            node_parser = LangchainNodeParser(RecursiveCharacterTextSplitter())
            nodes = node_parser.get_nodes_from_documents(
                [Document.from_file(path_to_data, show_progress=True)]
            )
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
    vector_store = PGVectorStore(
        connection_string=connection_string,
        async_connection_string=connection_string,
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
