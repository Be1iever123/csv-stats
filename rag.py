import os
import chromadb
import streamlit as st
from chromadb.utils import embedding_functions
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()
api_key=os.getenv("DEEPSEEK_API_KEY")

class LLMService:
    # 1. 装修队进场，需要拿着 api_key
    def __init__(self, api_key):
        # 填空：把 api_key 和 base_url 塞进这个盒子的私人口袋（self）里，并造一个叫 client 的手机
        self.client = OpenAI(
            api_key=api_key, 
            base_url="https://api.deepseek.com"
        )
    # 2. 定义第一个功能：改写问题
    def rewrite(self, question, history):
        # 1. 如果没历史，直接返回原问题
        if not history:
            return question
        # 2. 取最近 2 条
        recent_history = history[-2:]
        # 构造提示词（填空：让大模型结合历史，把当前问题变完整）
        prompt = f"""
        是一个查询改写助手。请根据以下历史对话：
        {recent_history}
        把用户的最新问题重写成一个完整、独立的问题，不要回答问题，只输出改写后的问题。
        最新问题：{question}
        """
        # 填空：用盒子里的手机打电话（注意 self）
        response = self.client.chat.completions.create(
            model="deepseek-flash",
            messages=[{"role": "user", "content": prompt}],
            stream=False
        )
        return response.choices[0].message.content
    # 3. 定义第二个功能：正式回答
    def chat(self, messages):
        # 填空：用盒子里的手机打电话，并且要流式输出 (stream=True)
        response = self.client.chat.completions.create(
            model="deepseek-flash",
            messages=messages,
            stream=True
        )
        return response

# 实例化：造一个名叫 llm_service 的对象
llm_service = LLMService(api_key=api_key)

@st.cache_resource
def get_collection(content_text):
    default_ef = embedding_functions.DefaultEmbeddingFunction()
    client_db = chromadb.Client()
# 1. 有则拿，无则建（绝对不报“已存在”或“不存在”的错）
    collection = client_db.get_or_create_collection(
        name="my_knowledge", 
        embedding_function=default_ef
    )
# 2. 拿到集合后，先把里面的旧 ID 全部查出来
    all_ids = collection.get(include=[])["ids"]
# 3. 如果里面有旧数据，全部删掉（防串台）
    if all_ids:
        collection.delete(ids=all_ids)
# 4. 下面的切片逻辑不变
    chunks = []
    for i in range(0, len(content_text), 100):
        chunk = content_text[i:i+100]
        chunks.append(chunk)
# 5. 存入新数据
    collection.upsert(documents=chunks, ids=[str(i) for i in range(len(chunks))])

    return collection

def query_rag(question, history, content_text):
    # 1. 先改写问题（换成了用盒子里的方法！）
    search_query = llm_service.rewrite(question, history)
    # 2. 拿数据库
    collection = get_collection(content_text)
    # 3. 用改写后的问题去查（这段不变）
    results = collection.query(
        query_texts=[search_query],
        n_results=1
    )
    relevant_chunk = results['documents'][0][0]
    # 4. 组装历史消息（这段不变）
    messages = []
    recent_history = history[-10:]
    for msg in recent_history:
        messages.append({
            "role": msg["role"],
            "content": msg["content"]
        })
        
    messages.append({
        "role": "user",
        "content": f"请根据以下资料回答：\n资料：{relevant_chunk}\n问题：{question}"
    })
    # 5. 直接调大模型（换成了用盒子里的 chat 方法！）
    response = llm_service.chat(messages)  # <--- 看这里，清爽了吧！不需要写 model、stream 了！
    # 6. 流式输出
    for chunk in response:
        if chunk.choices[0].delta.content is not None:
            yield chunk.choices[0].delta.content