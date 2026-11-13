import argparse
if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("file")
    args=parser.parse_args()
    chunks=[]
    with open(args.file,"r",encoding="utf-8")as f:
        content=f.read()
        for i in range(0,len(content),100):
            chunk=content[i:i+100]
            chunks.append(chunk)
        print(f"一共切了{len(chunks)}块")
        print("第一块：", chunks[0])
        print("最后一块：", chunks[-1])