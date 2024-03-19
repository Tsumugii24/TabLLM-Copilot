import os
import json
import requests
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())
baidu_access_token = os.environ['BAIDU_ACCESS_TOKEN']


def get_completion_baidu(prompt, temperature=0.1, access_token=baidu_access_token):
    """
    prompt: 对应的提示词
    temperature：温度系数
    access_token：已获取到的秘钥
    """

    # 接口文档 https://cloud.baidu.com/doc/WENXINWORKSHOP/s/clntwmv7t
    # ERNIE-4.0-8K  https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/completions_pro
    # ERNIE-3.5-8K  https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/completions
    url = f"https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/completions_pro?access_token={access_token}"
    # 配置 POST 参数
    payload = json.dumps({
        "system": "你是一位经验丰富的数据分析师",
        "messages": [
            {
                "role": "user",  # user prompt
                "content": "{}".format(prompt)  # 输入的 prompt
            }
        ],
        "temperature": temperature
    })
    headers = {
        'Content-Type': 'application/json'
    }
    # 发起请求
    response = requests.request("POST", url, headers=headers, data=payload)
    # 返回的是一个 Json 字符串
    js = json.loads(response.text)
    # print(js)
    return js["result"]


if __name__ == '__main__':
    prompt = "今天天气怎么样？"
    print(get_completion_baidu(prompt))
