import sys
from llm_sdk.baidu_llm import Baidu_LLM
from llm_sdk.spark_llm import Spark_LLM
from llm_sdk.zhipu_llm import ZhipuLLM
from langchain.chat_models import ChatOpenAI
from llm_sdk.call_llm import parse_llm_api_key


def model_to_llm(model: str = None, temperature: float = 0.0, appid: str = None, api_key: str = None,
                 spark_api_secret: str = None, baidu_secret_key: str = None):
    """
    星火：model,temperature,appid,api_key,api_secret
    百度：model,temperature,api_key,api_secret
    智谱：model,temperature,api_key
    OpenAI：model,temperature,api_key
    """
    if model in ["gpt-3.5-turbo", "gpt-3.5-turbo-16k-0613", "gpt-3.5-turbo-0613", "gpt-4", "gpt-4-32k"]:
        if api_key is None:
            api_key = parse_llm_api_key("openai")
        llm = ChatOpenAI(model_name=model, temperature=temperature, openai_api_key=api_key)
    elif model in ["ERNIE-4.0-8K", "ERNIE-3.5-8K", "ERNIE-3.5-8K-0205"]:
        if api_key is None or baidu_secret_key is None:
            api_key, baidu_secret_key = parse_llm_api_key("baidu")
        llm = Baidu_LLM(model=model, temperature=temperature, api_key=api_key, secret_key=baidu_secret_key)
    elif model in ["Spark-3.5", "Spark-3.0"]:
        if api_key is None or appid is None and spark_api_secret is None:
            api_key, appid, spark_api_secret = parse_llm_api_key("spark")
        llm = Spark_LLM(model=model, temperature=temperature, appid=appid, api_secret=spark_api_secret, api_key=api_key)
    elif model in ["glm-4", "glm-4v", "glm-3-turbo"]:
        if api_key is None:
            api_key = parse_llm_api_key("zhipu")
        llm = ZhipuLLM(model=model, zhipuai_api_key=api_key, temperature=temperature)
    else:
        raise ValueError(f"model{model} not support!!!")
    return llm
