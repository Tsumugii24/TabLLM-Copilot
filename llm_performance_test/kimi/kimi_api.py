import os
from openai import OpenAI
from config.config import config
from dotenv import load_dotenv, find_dotenv

# 读取本地/项目的环境变量。

# find_dotenv()寻找并定位.env文件的路径
# load_dotenv()读取该.env文件，并将其中的环境变量加载到当前的运行环境中

load_dotenv(find_dotenv())

# 如果你需要通过代理端口访问，你需要如下配置
# os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:7890'
# os.environ["HTTP_PROXY"] = 'http://127.0.0.1:7890'

# 获取环境变量 OPENAI_API_KEY 并实例化 OpenAI
# client = OpenAI(api_key=os.environ['OPENAI_API_KEY'], base_url=os.environ['OPENAI_BASE_URL'])
client = OpenAI(api_key=os.environ['KIMI_API_KEY'], base_url=os.environ['KIMI_BASE_URL'])


# 一个封装 OpenAI 接口的函数，参数为 Prompt，返回对应结果
def get_completion_kimi(prompt, model="moonshot", temperature=0):
    """
    prompt: 对应的提示词
    model: 调用的模型，默认为 gpt-3.5-turbo，也可以选择 gpt-3.5-turbo-16k 或 gpt-4 或 gpt-4o
    """

    # 构造消息
    messages = [
        {"role": "system", "content": config.system_prompt},
        {"role": "user", "content": [
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": {
                "url": "https://cdn.jsdelivr.net/gh/Tsumugii24/Typora-images@main/images/2024/05/18/6b18fbc069b11bb4712e0c2139b1771d-image-20240518211658568-0e34d3.png"}
             }
        ]}
    ]

    # 调用 ChatCompletion 接口
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,  # 模型输出的温度系数，控制输出的随机程度
    )

    return response.choices[0].message.content


if __name__ == '__main__':
    prompt = config.user_prompt
    print(get_completion_kimi(prompt))
