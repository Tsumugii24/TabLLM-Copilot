import os
import openai
from dotenv import load_dotenv, find_dotenv

from langchain_openai import ChatOpenAI  # from langchain.chat_models import ChatOpenAI (deprecated
from langchain.prompts import ChatPromptTemplate

load_dotenv(find_dotenv())

# 配置通过代理端口访问
os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:7890'
os.environ["HTTP_PROXY"] = 'http://127.0.0.1:7890'
# 获取环境变量 OPENAI_API_KEY
openai.api_key = os.environ['OPENAI_API_KEY']

# 这里我们要求模型对给定文本进行中文翻译
template_string = """Translate the text \
that is delimited by triple backticks \
into a Chinese. \
text: ```{text}```
"""

# 接着将 Template 实例化
chat_template = ChatPromptTemplate.from_template(template_string)

# 我们首先设置变量值
text = "Today is a nice day."

# 接着调用 format_messages 将 template 转化为 message 格式
message = chat_template.format_messages(text=text)
print(message)

get_completion_openai = ChatOpenAI(temperature=0.0)
response = get_completion_openai(message)
print(response)
