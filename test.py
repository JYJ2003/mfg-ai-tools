import os
import json
import time
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://ws-q8hhhd9xvle4ilo1.cn-beijing.maas.aliyuncs.com/compatible-mode/v1"
)

def extract(text):
    system_prompt = (
        "你是信息抽取助手，只输出JSON,不要任何解释。\n" 
        "格式必须严格如下：\n" 
        '{"设备":"","异常类型":"","等级":"高/中/低","建议动作":""}'
    )

    for attempt in range(2):
        try:
            r = client.chat.completions.create(
                model="qwen3.7-plus",
                response_format={"type":"json_object"},
                messages=[
                    {"role":"system","content":system_prompt},
                    {"role":"user","content":f"<data>{text}</data>"},
                ],
                temperature=0.1
            )

            raw_content = r.choices[0].message.content
            return json.loads(raw_content)

        except json.JSONDecodeError as e:
            print(f"!!!第{attempt+1}次解析失败，错误原因：{e}")
            print(f"原始输出：{raw_content}")

            if attempt == 0:
                print("正在进行重试...\n")
                time.sleep(1)
            else:
                print("重试依然失败，放弃解析。")
                return{"error":str(e),"raw":raw_content}


# --- 验收测试：跑 5 条不同描述 ---
if __name__ == "__main__":
    test_texts = [
        "3号线贴标机偏移，连续5件不良，需停机校正",                          # 标准
        "2号装配线气压不足导致机械臂停顿，情况非常紧急，立刻安排检修",       # 带有情绪和紧急程度
        "5号包装机偶尔卡纸，影响轻微，建议生产结束后清理",                  # 轻微问题
        "1号焊接机器人焊点偏移，发现3件次品，需要重新调整参数",              # 工艺参数
        "4号线物料输送带断裂，全线停产，需紧急抢修"                         # 严重故障
    ]

    print("===== 开始验收测试 =====")
    for i,text in enumerate(test_texts,1):
        print(f"\n--- 测试 {i} ---")
        print(f"输入: {text}")
        result = extract(text)
        print(f"输出: {result}")
