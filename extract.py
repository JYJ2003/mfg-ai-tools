import os
import json
import time
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# 保持你配置好的百炼专属 Base URL
client = OpenAI(
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://ws-q8hhhd9xvle4ilo1.cn-beijing.maas.aliyuncs.com/compatible-mode/v1"
)

def extract(text):
    # 1. 在 system 里写死 JSON 骨架，明确要求“只输出JSON”
    system_prompt = (
        "你是信息抽取助手，只输出JSON，不要任何解释。\n"
        "格式必须严格如下：\n"
        '{"设备":"","异常类型":"","等级":"高/中/低","建议动作":""}'
    )
    
    # 2. 增加重试机制（满足“失败就打印原文再重试一次”）
    for attempt in range(2):
        try:
            # 3. 调用 API，使用 response_format 强制 JSON
            r = client.chat.completions.create(
                model="qwen3.7-plus",
                response_format={"type": "json_object"}, # 关键参数，强约束输出格式
                messages=[
                    {"role": "system", "content": system_prompt},
                    # 使用之前学的“分隔符”，防止数据与指令串扰
                    {"role": "user", "content": f"<data>{text}</data>"}, 
                ],
                temperature=0.1 # 抽取任务需要极度严谨，温度设低一点
            )
            
            raw_content = r.choices[0].message.content
            # 尝试解析 JSON
            return json.loads(raw_content)
            
        except json.JSONDecodeError as e:
            # 解析失败，打印原文和错误
            print(f"⚠️ 第 {attempt + 1} 次解析失败，错误原因: {e}")
            print(f"📄 原始输出: {raw_content}")
            
            if attempt == 0:
                print("🔄 正在进行重试...\n")
                time.sleep(1) # 稍微等一下，避免并发限制
            else:
                print("❌ 重试依然失败，放弃解析。")
                return {"error": str(e), "raw": raw_content}

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
    for i, text in enumerate(test_texts, 1):
        print(f"\n--- 测试 {i} ---")
        print(f"输入: {text}")
        result = extract(text)
        print(f"输出: {result}")