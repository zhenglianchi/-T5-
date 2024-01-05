import torch,os
from flask_cors import CORS
from flask import Flask, request, jsonify
from transformers import AutoTokenizer, T5ForConditionalGeneration
from model import  T5ForMultimodalGeneration
import numpy as np
import timm
from PIL import Image
from timm.data import resolve_data_config
from timm.data.transforms_factory import create_transform


le_tokenizer = AutoTokenizer.from_pretrained("models/rationale")
le_model = T5ForConditionalGeneration.from_pretrained("models/rationale")
ans_tokenizer = AutoTokenizer.from_pretrained("models/answer")
ans_model = T5ForMultimodalGeneration.from_pretrained("models/answer", patch_size=(145, 1024))
vit_model = timm.create_model("vit_large_patch32_384", pretrained=True, num_classes=0)
vit_model.eval()
app = Flask(__name__)
CORS(app)

def extract_features(input_image):
    config = resolve_data_config({}, model=vit_model)
    transform = create_transform(**config)
    with torch.no_grad():
        img = Image.open(input_image).convert("RGB")
        input = transform(img).unsqueeze(0)
        feature = vit_model.forward_features(input)
    return feature

def get_le(prompt):
    prompt = prompt + "\nSolution:"
    input_ids = le_tokenizer(prompt, return_tensors="pt").input_ids
    outputs = le_model.generate(input_ids,max_length=512)
    le = le_tokenizer.decode(outputs[0], skip_special_tokens=True)
    return le

def get_ans(le,prompt,have_pic=False,input_image=None):
    prompt = prompt + le + "\nAnswer:"
    input_ids = ans_tokenizer(prompt, return_tensors="pt").input_ids

    if have_pic:
        image_ids = extract_features(input_image)
    else:
        image_ids = np.zeros((145, 1024))
    image_ids = torch.FloatTensor(image_ids).squeeze()
    image_ids = image_ids.unsqueeze(0)

    outputs = ans_model.generate(input_ids,image_ids=image_ids,max_length=512)
    ans = ans_tokenizer.decode(outputs[0], skip_special_tokens=True)
    return ans



@app.route('/chat', methods=['GET'])
def chat():
    R={}
    prompt = str(request.args["message"])
    have_pic=False
    filename = "image.png"
    input_image=None
    if os.path.exists(filename):
        have_pic = True
        input_image=filename
        
    le = get_le(prompt)
    R["le"]=le
    ans = get_ans(le,prompt,have_pic,input_image)
    R["ans"]=ans
    return jsonify(R)

if __name__ == "__main__":
    app.run(port=80,debug = False)

