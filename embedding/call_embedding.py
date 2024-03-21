from embedding.zhipu_embedding import ZhipuAIEmbeddings
from langchain.embeddings.huggingface import HuggingFaceEmbeddings
from langchain.embeddings.openai import OpenAIEmbeddings
from llm_sdk.call_llm import parse_llm_api_key


def get_embedding(embedding: str, embedding_key: str = None):
    if embedding_key is None:
        embedding_key = parse_llm_api_key(embedding)
    if embedding == "openai":
        return OpenAIEmbeddings(openai_api_key=embedding_key)
    elif embedding == "zhipu":
        return ZhipuAIEmbeddings(zhipu_api_key=embedding_key)
    elif embedding == 'm3e':  # https://huggingface.co/moka-ai/m3e-base
        return HuggingFaceEmbeddings(model_name="moka-ai/m3e-base")
    elif embedding == 'gte':  # https://huggingface.co/thenlper/gte-base-zh
        return HuggingFaceEmbeddings(model_name="thenlper/gte-base-zh")
    else:
        raise ValueError(f"embedding {embedding} not support ")
