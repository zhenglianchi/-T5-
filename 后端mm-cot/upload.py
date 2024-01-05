from flask_cors import CORS
from flask import Flask, request, jsonify
import os

app = Flask(__name__)
CORS(app)

def rename_file(old_name, new_name):
    try:
        os.rename(old_name, new_name)
        print(f"File renamed from {old_name} to {new_name} successfully.")
    except OSError as e:
        print(f"Error renaming file: {e}")

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file:
        file.save("../jeecg-boot-v3.4.0/ant-design-vue-jeecg/src/views/chat/image.png")
        file.seek(0)
        file.save("image.png")
        return jsonify({'message': 'File uploaded successfully'}), 200

    return jsonify({'error': 'Invalid file type'}), 400

@app.route('/clear', methods=['POST'])
def clear():
    file_path="./image.png"
    try:
        os.remove(file_path)
        return jsonify({'message': 'File clear successfully'}), 200
    except OSError as e:
        return jsonify({'message': 'Error deleting file {file_path}'}), 400


if __name__ == "__main__":
    app.run(port=90,debug = False)

