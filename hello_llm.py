import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("DASHSCOPE_API_KEY"), 
    # 直接复制你截图里专属的 Base URL
    base_url="https://ws-q8hhhd9xvle4ilo1.cn-beijing.maas.aliyuncs.com/compatible-mode/v1"
)

resp = client.chat.completions.create(
    model="qwen3.7-plus",
    messages=[{"role": "user", "content": "用一句话解释什么是Few-shot"}],
)
print(resp.choices[0].message.content)