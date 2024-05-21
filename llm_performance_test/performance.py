from baidu.baidu_api import get_completion_baidu
from myopenai.openai_api import get_completion_openai
from sparkdesk.spark_api import get_completion_spark
from zhipu.zhipu_api import get_completion_zhipu

table = """
Methods	R	P	F	FPS
SegLink[26]	70.0	86.0	77.0	8.9
PixelLink [4]	73.2	83.0	77.8	
TextSnake[18]	73.9	83.2	78.3	1.1
TextField [37]	75.9	87.4	81.3	5.2
MSR[38]	76.7	87.4	81.7	-
FTSN [3]	77.1	87.6	82.0	-
LSE[30]	81.7	84.2	82.9	-
CRAFT [2]	78.2	88.2	82.9	8.6
MCN[16]	79	88	83	-
ATRR[35]	82.1	85.2	83.6	
PAN [34]	83.8	84.4	84.1	30.2
DB[12]	79.2	91.5	84.9	32.0
DRRG [41]	82.30	88.05	85.08	
Ours (SynText)	80.68	85.40	82.97	12.68
Ours (MLT-17)	84.54	86.62	85.57	12.31
"""  # 示例表格数据
prompt = """
请帮我生成一段关于以下用```符号包括的表格数据的详细分析
table: ```{table}```
""".format(table=table)

print("temperature: 0.1")
print("system:", "你是一位经验丰富的数据分析师。")
print("prompt:", prompt)
print("\n")

# ernie_4_8k_response = get_completion_baidu(prompt)  # 欠费
# gpt_35_turbo = get_completion_openai(prompt)
spark_v35 = get_completion_spark(prompt)
glm_4 = get_completion_zhipu(prompt)

# print("百度 ERNIE-4.0-8K: ", ernie_4_8k_response + "\n")
# print("OpenAI GPT-3.5-turbo: ", gpt_35_turbo + "\n")
print("SparkDesk V3.5: ", spark_v35 + "\n")
print("ZhipuAI glm-4: ", glm_4 + "\n")
