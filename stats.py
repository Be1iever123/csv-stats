import argparse
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("file")
    args = parser.parse_args()

    with open(args.file, "r", encoding="utf-8") as f:
        f.readline()
        total_age=0
        total_score=0
        count_age=0
        count_score=0
        for line in f:
            parts=line.strip().split(",")
            age=parts[1]
            score=parts[2]
            if age!="":
                try:
                    age_num=int(age)
                    total_age=total_age+age_num
                    count_age=count_age+1
                except ValueError:
                    print(f"发现非数字数据，已跳过：{age}")
            if score!="":
                try:
                    score_num=int(score)
                    total_score=total_score+score_num
                    count_score=count_score+1
                except ValueError:
                    print(f"发现非数字数据，已跳过：{score}")
    average_age=total_age/count_age
    print(f"总人数:{count_age},平均年龄:{average_age}")
    average_score=total_score/count_score
    print(f"总人数:{count_score},平均分数:{average_score}")