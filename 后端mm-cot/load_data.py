#load_data.py
import json
import numpy as np
import os
import torch
import re
#得到question
def get_question_text(problem):
    question = problem['question']
    return question

#得到提示和图片描述并拼接为字符串即Context，如果无则为N/A
def get_context_text(problem, use_caption):
    txt_context = problem['hint']
    img_context = problem['caption'] if use_caption else ""
    #去除空格
    context = " ".join([txt_context, img_context]).strip()
    if context == "":
        context = "N/A"
    return context

#得到所有的选项(包括但不限于正确答案)
def get_choice_text(probelm, options):
    choices = probelm['choices']
    choice_list = []
    for i, c in enumerate(choices):
        choice_list.append("({}) {}".format(options[i], c))
    choice_txt = " ".join(choice_list)
    #print(choice_txt)
    return choice_txt

#得到初始答案即答案的文字
def get_origin_answer(problem):
    return problem['choices'][problem['answer']]

#得到答案选项即ABCDE
def get_answer(problem, options):
    return options[problem['answer']]

#得到其课程信息并去除换行
def get_lecture_text(problem):
    # \\n: GPT-3 can generate the lecture with more tokens.
    lecture = problem['lecture'].replace("\n", "\\n")
    return lecture

#得到其推理内容并去除换行
def get_solution_text(problem):
    # \\n: GPT-3 can generate the solution with more tokens
    solution = problem['solution'].replace("\n", "\\n")
    return solution

def extract_ans(ans):
    pattern = re.compile(r'[A-Z]')
    res = pattern.findall(ans)
    
    if len(res) != 1:
        answer = res[1]  # 'A', 'B', ...
    else:
        answer = "FAILED" 
    return answer  

def create_one_example(question, context, choice, le="", have_le=False):
    if have_le:
        input = f"Question: {question}\nContext: {context}\nOptions: {choice}\n{le}\n"

        output = "Answer:"

        text = input + output
        text = text.replace("  ", " ").strip()
        output = output.replace("  ", " ").strip()
        return text,output

    input = f"Question: {question}\nContext: {context}\nOptions: {choice}\n"

    output = f"Solution: "

    text = input + output
    text = text.replace("  ", " ").strip()
    output = output.replace("  ", " ").strip()
    return text,output

def init_data(question_num,have_le=False):
    image_features = torch.load("vision_features/vit.pth")
    captions = json.load(open("data/captions.json"))["captions"]
    problems = json.load(open(os.path.join("data", 'scienceqa/problems.json')))
    name_maps = json.load(open('vision_features/name_map.json'))
    for qid in problems:
        problems[qid]['caption'] = captions[qid] if qid in captions else ""


    options=["A", "B", "C", "D", "E"]
    question = get_question_text(problems[str(question_num)])
    context = get_context_text(problems[str(question_num)], True)
    choice = get_choice_text(problems[str(question_num)], options)
    lecture = get_lecture_text(problems[str(question_num)])
    solution = get_solution_text(problems[str(question_num)])
    test_example,target = create_one_example(question,context,choice,lecture+solution,have_le)

    if str(question_num) in name_maps:
        image_ids = image_features[int(name_maps[str(qid)])]
    else:
        image_ids = np.zeros((145, 1024))

    image_ids = torch.FloatTensor(image_ids).squeeze()

    return test_example,target,image_ids

