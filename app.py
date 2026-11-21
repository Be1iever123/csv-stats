import streamlit as st
from rag import query_rag
import json
import os

def save_history():
    with open("history.json", "w", encoding="utf-8") as f:
        json.dump(st.session_state.messages, f, ensure_ascii=False, indent=4)

if "messages" not in st.session_state:
    # 看看硬盘上的 json 文件有没有
    if os.path.exists("history.json"):
        with open("history.json", "r", encoding="utf-8") as f:
            st.session_state.messages = json.load(f)
    else:
        st.session_state.messages = []

st.title("我的RAG知识库")
# 初始化一个计数器，用来当做上传框的钥匙
if 'uploader_key' not in st.session_state:
    st.session_state.uploader_key = 0
# --- 积木1：清空按钮 ---
if st.sidebar.button("🗑️ 清空对话记录"):
    # 1. 清空脑子里的记忆
    st.session_state.messages = []
    # 把数字钥匙+=1，这样上传框就找不到旧钥匙了
    st.session_state.uploader_key+=1
    # 2. 如果硬盘里有文件，就删掉
    if os.path.exists("history.json"):
        os.remove("history.json")
    # 3. 刷新页面
    st.rerun()
# --- 积木2：下载按钮 ---
if st.session_state.messages: # 如果有聊天记录，才显示下载按钮
    # 1. 把聊天记录变成一大段文字
    chat_text = ""
    for msg in st.session_state.messages:
        chat_text += f"{msg['role']}说: {msg['content']}\n\n"  
    # 2. 画个下载按钮
    st.sidebar.download_button(
        label="📥 下载对话记录",
        data=chat_text,
        file_name="我的对话记录.txt",
        mime="text/plain"
    )
# 1. 造一个上传文件的按钮
# 注意看 key 的地方，变成了 f-string（动态拼接）
uploaded_file = st.file_uploader("请上传你的数据文件（CSV格式）", type=["csv"], key=f"csv_uploader_{st.session_state.uploader_key}")
# 2. 如果用户真的传了文件
if uploaded_file is not None:
    # 3. 拿到文件的二进制数据（电脑底层存的都是0101）
    bytes_data = uploaded_file.getvalue()
    # 4. 把二进制解码成人类能看懂的文字
    text_data = bytes_data.decode("utf-8") 
    # 5. 在网页上展示前 100 个字，看看读对没
    st.write("文件读取成功，预览前100个字符：")
    st.write(text_data[:100])

prompt=st.chat_input("请输入你的问题")
#1.遍历记忆里的所有消息，画在屏幕上
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
#2.如果用户发来新消息
if prompt:
    # 兜底判断：如果没传文件，警告并拦截 
    if uploaded_file is None:
        st.warning("请先上传文件，再开始提问")
        st.stop()
    else: 
        #先把用户消息追加到记忆里
        st.session_state.messages.append({"role":"user","content":prompt})
        save_history()
        #然后再画出来（其实上面的for循环下一次重跑时会画，但为了及时反馈，这里立刻画一次）
        with st.chat_message("user"):
            st.write(prompt)
        with st.chat_message("assistant"):
            with st.spinner("正在翻阅知识库..."):
                # 把当前的问题 prompt，以及之前的历史 st.session_state.messages[:-1] 传进去
                # 为什么用 [:-1]？因为上面刚 append 过这一次的 prompt，传进去防止重复。
                answer = st.write_stream(query_rag(prompt, st.session_state.messages[:-1],text_data))
    #把AI的回答也存进记忆里
    st.session_state.messages.append({"role":"assistant","content":answer})
    save_history()