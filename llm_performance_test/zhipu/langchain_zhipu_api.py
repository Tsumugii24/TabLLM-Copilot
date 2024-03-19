import os

from dotenv import load_dotenv, find_dotenv
from langchain_zhipu import ChatZhipuAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv(find_dotenv())
zhipu_api_key = os.environ['ZHIPU_API_KEY']

llm = ChatZhipuAI(temperature=0.1, api_key=zhipu_api_key, model_name="glm-4")

prompt = ChatPromptTemplate.from_messages([
    ("system", "你是编程大师。"),
    ("user", "{input}")
])

output_parser = StrOutputParser()
# print(llm_sdk.invoke("langsmith如何帮助测试?"))
chain = prompt | llm | output_parser
print(chain.invoke({"input": "帮我写一段python代码。"}))
