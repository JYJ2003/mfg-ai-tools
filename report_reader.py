import os
from dotenv import load_dotenv
from openai import OpenAI
import pandas as pd
import argparse

load_dotenv()

parser = argparse.ArgumentParser(description="生产日报分析工具")
parser.add_argument("file", nargs="?", default="生产日报.xlsx", help="日报文件路径")
args = parser.parse_args()

client = OpenAI(
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://ws-q8hhhd9xvle4ilo1.cn-beijing.maas.aliyuncs.com/compatible-mode/v1"
)

df = pd.read_excel(args.file)
summary_desc = df.describe().to_string()
# 使用 groupby 按线体计算，注意：良率求平均（mean），产量和停机时长求和（sum）
summary_group = df.groupby('线体').agg({
    '产量': 'sum',
    '良率': 'mean',   # 良率求平均，不能求和
    '停机时长': 'sum'
}).round(3).to_string()

def ask(prompt,system="你是一名有着20年经验的制造业总监，你的回答必须基于数据，严谨真实，严禁造假和空话"):
    r = client.chat.completions.create(
        model="qwen3.7-plus",
        messages=[
            {"role":"system","content":system},
            {"role":"user","content":prompt}
        ],
        temperature=0.2
    )
    return r.choices[0].message.content

# 4. 拼接 Prompt
prompt = f"""以下是一份生产日报数据统计，请你作为生产总监进行分析：

【全局数据概览】：
{summary_desc}

【各线体分组统计】：
{summary_group}

请完成以下任务：
1. 指出最异常的 1-2 个指标（必须说明具体是哪条线体、具体数据是多少、对比其他线体为何异常）。
2. 给出 3 条可执行的改进建议（请针对异常指标，给出具体的动作，如“建议排查3号线贴标机传感器”这样具体的内容，严禁说“加强管理”等空话）。
3. 用表格输出你的分析结论。

请严格按上述格式输出。
"""

# 5. 调用大模型并打印
print("🤖 正在分析日报...\n")
result = ask(prompt)
print(result)