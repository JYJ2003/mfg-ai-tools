import csv
import os
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://ws-q8hhhd9xvle4ilo1.cn-beijing.maas.aliyuncs.com/compatible-mode/v1"
)

# 1. 改造 ask 函数，强制 JSON 输出
def ask(prompt, system="你是一名严谨的工业异常分类助手，只输出JSON，不要任何解释。"):
    r = client.chat.completions.create(
        model="qwen3.7-plus",
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": prompt}
        ],
        response_format={"type": "json_object"},  # 👈 关键锁死！
        temperature=0.1
    )
    return r.choices[0].message.content

# 2. 改造阅卷机，因为现在返回的是 JSON 字符串
def evaluate(build_prompt):
    total = correct = 0
    for row in csv.DictReader(open("test_cases.csv", encoding="utf-8")):
        total += 1
        try:
            out_raw = ask(build_prompt(row["描述"]))
            out_dict = json.loads(out_raw)
            pred_label = out_dict.get("标签", "解析失败")
        except Exception as e:
            pred_label = f"解析异常: {e}"
            
        if row["正确标签"] in pred_label:
            correct += 1
        else:
            print(f"❌ 错例：输入[{row['描述']}] 期望[{row['正确标签']}] 实际[{pred_label}]")
            
    return correct / total if total else 0

# 3. 优化 Prompt（把关键规则写死）
v3 = lambda d: (
    "请将输入描述严格分类为以下四类之一：【设备故障】【物料问题】【工艺问题】【其他】。\n\n"
    "判分规则（重要！）：\n"
    "1. 机械松动、传感器脏污、电气损坏、电机烧毁 → 设备故障。\n"
    "2. 参数设置错误、调试不准、速度不匹配、贴标机偏移、焊接轨迹偏差 → 工艺问题。\n"
    "3. 缺料、来料不良、送料延迟 → 物料问题。\n\n"
    "示例1：\n描述：机械臂突然停止运作，无法启动\n输出：{\"标签\": \"设备故障\"}\n\n"
    "示例2：\n描述：贴标机参数设置错误，导致连续偏移\n输出：{\"标签\": \"工艺问题\"}\n\n"
    f"现在请判断：\n描述：{d}\n输出："
)

print("v3 准确率：", round(evaluate(v3), 2))