<template>
  <div class="chat-container">
    <div class="message-container">
      <ul ref="messageList" class="message-list">
        <li v-for="(message, index) in messages" :key="index" :class="getMessageClasses(message)" class="message">
          <div v-if="message.userType === 'user'">
            <img src="./user.png" alt="User Avatar" class="avatar" /> <!-- 用户头像 -->
            <span class="user-tag">zhenglianchi</span>
          </div>
          <div v-else>
            <img src="./system.png" alt="System Avatar" class="avatar" /> <!-- 系统头像 -->
            <span class="user-tag">人工智障</span>
          </div>
          {{ message.text }}
        </li>
      </ul>
      <div v-if="loading" class="loading-indicator"></div>
    </div>

    <div class="input-container">
      <input v-model="message" placeholder="输入消息..." @keyup.enter="sendMessage" />
      <button @click="sendMessage">发送</button>
      <button @click="clearConversation">清除对话</button>
    </div>
    <div>
      <input type="file" @change="handleFileChange" ref="fileInput"/>
      <button @click="uploadFile">上传图片</button>
      <button @click="clearImage">清除图片</button>
    </div>
    <div v-if="this.uploadedImage">
      <img src="./image.png" class="bottom-image"/>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'Chat',
  data() {
    return {
      message: '',
      temp: '',
      messages: JSON.parse(localStorage.getItem('chatMessages')) || [],
      nextMessageId: 1,
      loading: false,
      selectedFile: null,
      uploadedImage: null,
    };
  },
  methods: {
    handleFileChange(event) {
      this.selectedFile = event.target.files[0];
    },
    uploadFile() {
      if (this.selectedFile) {
        const formData = new FormData();
        formData.append('file', this.selectedFile);

        // 使用axios发送文件上传请求
        // 替换下面的URL为你的后端上传接口
        axios.post('http://127.0.0.1:90/upload', formData)
          .then(response => {
            // 保存上传成功的图片链接
            this.uploadedImage = true;
            // 清空selectedFile，以便下次上传
            this.$refs.fileInput.value = null;
            this.selectedFile = null;
          })
          .catch(error => {
            console.error(error);
          });
      }
    },
    clearImage() {
        axios.post('http://127.0.0.1:90/clear')
          .then(response => {
            this.uploadedImage = false;
            this.selectedFile = null;
          })
          .catch(error => {
            console.error(error);
          });
      },
    getMessageClasses(message) {
      return {
        'user': message.userType === 'user',
        'bot': message.userType === 'system',
      };
    },
    sendMessage() {
      if (this.message.trim() === '') return;
      this.messages.push({ id: this.nextMessageId++, text: this.message, userType: 'user' });
      this.temp = this.message;
      this.message = '';
      this.loading = true;
      this.convert();
    },
    convert() {
      axios
        .get('http://127.0.0.1:80/chat', {
          params: {
            message: this.temp,
          },
        })
        .then((res) => {
          this.messages.push({ id: this.nextMessageId++, text: res.data.le, userType: 'system' });
          this.messages.push({ id: this.nextMessageId++, text: res.data.ans, userType: 'system' });
          this.$nextTick(() => {
            this.scrollToBottom();
          });
        })
        .finally(() => {
          this.loading = false;
          this.saveToLocalStorage();
        });
    },
    saveToLocalStorage() {
      localStorage.setItem('chatMessages', JSON.stringify(this.messages));
    },
    clearConversation() {
      this.messages = [];
      localStorage.removeItem('chatMessages');
    },
    scrollToBottom() {
      const messageList = this.$refs.messageList;
      if (messageList) {
        messageList.scrollTop = messageList.scrollHeight;
      }
    },
  },
};
</script>

<style scoped>
.chat-container {
  max-width: 50%;
  margin: 0 auto;
  border: none;
}

.message-container {
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 50px; /* Distance from the bottom */
  overflow-y: auto;
  max-height: 300px;
}

.message {
  list-style: none;
  padding: 8px;
  margin-bottom: 8px;
  border-radius: 4px;
  max-width: 70%;
}

.message.user {
  background-color: yellowgreen;
  color: #fff;
  text-align: right;
  margin-left: auto;
}

.message.bot {
  background-color: grey;
  margin-right: auto;
}

.message-list {
  overflow-y: auto;
}

.input-container {
  display: flex;
  align-items: center; /* 将内容垂直居中对齐 */
  margin-bottom: 10px; /* Distance from the bottom */
}

input {
  flex: 1;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  margin-right: 8px;
}

button {
  padding: 8px 16px;
  border: none;
  background-color: #4caf50;
  color: #fff;
  border-radius: 4px;
  cursor: pointer;
}

.loading-indicator {
  border: 4px solid #f3f3f3;
  border-top: 4px solid #3498db;
  border-radius: 50%;
  width: 16px;
  height: 16px;
  animation: spin 1s linear infinite;
  margin: 16px auto;
}

.avatar {
  width: 24px;
  height: 24px;
  margin-right: 8px;
}
.bottom-image {
  max-width: 480px;  /* 设置最大宽度为父元素的宽度 */
  max-height: 240px;  /* 设置最大高度，根据需要调整 */
  margin-top: 10px;  /* 调整图片与上方内容的间距 */
}

.user-tag {
  font-weight: bold;
}
</style>
