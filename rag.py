import os
import argparse
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()
api_key=os.getenv("DEEPSEEK_API_KEY")
client=OpenAI(
    api_key=api_key,
    base_url="https://api.deepseek.com"
)
if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("file")
    args=parser.parse_args()

    with open(args.file,"r",encoding="utf-8")as f:
        content=f.read()
        chunks=[]
        for i in range(0,len(content),100):
            chunk=content[i:i+100]
            chunks.append(chunk)
        question=input("你的问题是： ")
        relevant_chunk = "未找到相关资料"
        for chunk in chunks:
            if "学号" in chunk:
                relevant_chunk=chunk
        response=client.chat.completions.create(
            model="deepseek-flash",
            messages=[
                {"role":"user","content":f"请根据以下资料回答：\n资料:{relevant_chunk}\n问题:{question}"}
            ]
        )
    print(response.choices[0].message.content)