import os
from openai import OpenAI
from dotenv import load_dotenv

# 1. 加载 Key
load_dotenv()
api_key = os.getenv("DEEPSEEK_API_KEY")

# 2. 创建客户端
client = OpenAI(
    api_key=api_key,
    base_url="https://api.deepseek.com"
)

# 3. 准备一个空列表，用来存储聊天记录
messages = []

print("🤖 欢迎使用 Chat-CLI！输入 'exit' 退出。")

# 4. 开启死循环，不断接收输入
while True:
    user_input = input("\n你: ")
    
    # 如果输入 exit，则跳出循环结束程序
    if user_input.lower() == 'exit':
        print("👋 再见！")
        break
    
    # 把用户的话存入历史记录
    messages.append({"role": "user", "content": user_input})
    
    # 发送请求（带上所有历史记录）
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages
    )
    
    # 提取 AI 的回答
    ai_reply = response.choices[0].message.content
    
    # 把 AI 的回答也存入历史记录，以便下次对话时它能记住
    messages.append({"role": "assistant", "content": ai_reply})
    
    # 打印 AI 的回答
    print(f"\n🤖 AI: {ai_reply}")