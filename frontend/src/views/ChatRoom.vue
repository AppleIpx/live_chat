<template>
  <div class="chat">
    <div class="chat-container">
      <!-- Chat Header -->
      <div class="chat-header">
        <button @click="goBack" class="back-button">
          <i class="fa fa-arrow-left"></i>
        </button>

        <!-- Chat Info -->
        <div class="chat-info">
          <span v-if="chatData">
            <span
                v-if="chatData.chat_type === 'group'"
                class="group-name"
                @mouseover="showGroupTooltip = true"
                @mouseleave="onGroupMouseLeave"
            >
              {{ chatData.name_group }}
            </span>
            <div
                v-if="showGroupTooltip"
                class="group-tooltip"
                @mouseover="showGroupTooltip = true"
                @mouseleave="onTooltipMouseLeave"
            >
              <ul>
                <li v-for="user in chatData.users" :key="user.id" class="tooltip-user">
                  <a v-if="user && user.id"
                     :href="user.username === this.user.username ? '/profile/me' : '/profile/' + user.id">
                    <img v-if="user.user_image" :src="user.user_image"
                         alt="User Avatar" class="user-avatar">
                    {{ user.first_name }} {{ user.last_name }}
                  </a>
                </li>
              </ul>
              <div class="tooltip-actions">
                <button class="tooltip-button"
                        @click.prevent>Изменить название (заглушка)</button>
                <div>
                  <button class="tooltip-button" @click.prevent="openImageUploadModal">
                    Изменить фото
                  </button>
                  <div v-if="isImageUploadModalOpen" class="modal-overlay">
                    <div class="modal-content">
                      <h2>Загрузить фото группы</h2>
                      <div class="group-image-upload">
                        <input type="file" @change="handleImageUpload"/>
                        <div v-if="groupImagePreview" class="image-preview">
                          <img :src="groupImagePreview" alt="Preview"/>
                        </div>
                      </div>
                      <div class="modal-actions">
                        <button @click="uploadGroupImage">Загрузить</button>
                        <button @click="closeImageUploadModal">Отмена</button>
                      </div>
                    </div>
                  </div>
                </div>
            </div>
            </div>
            <span v-if="chatData.chat_type==='direct'">{{ chatName }}</span>
          </span>
        </div>

        <div class="chat-photo">
          <template
              v-if="chatData && chatData.chat_type === 'group' && chatData.image_group">
            <img :src="chatData.image_group" alt="Group image"/>
          </template>
          <template v-else-if="chatData && otherUser && otherUser.user_image">
            <a :href="`/profile/${otherUser.id}`">
              <img :src="otherUser.user_image" alt="Profile"/>
            </a>
          </template>
        </div>
      </div>

      <!-- Messages Section -->
      <div class="messages-container">
        <div v-if="messages.length" class="messages-list" ref="messagesList">
          <div class="message" v-for="message in messages" :key="message.id"
               :class="{'mine': message.isMine, 'other': !message.isMine}">
            <div class="message-header">
              <strong>
                <a v-if="message.user || message.user_id"
                   :href="message.user.username === user.username ? '/profile/me' : '/profile/' + message.user.id">
                  {{ message.user.id === user.id ? 'Вы' : message.user.username }}
                </a>
                <span v-else>Загрузка...</span>
              </strong>
              <span class="timestamp">{{ message.created_at }}</span>
            </div>
            <div class="message-content">{{ message.content }}</div>
          </div>
        </div>
        <div v-else>
          <p class="no-messages">Нет сообщений...</p>
        </div>
      </div>

      <!-- Message Input -->
      <div class="chat-input-container">
        <textarea
            v-model="messageText"
            @keydown.enter="sendMessage"
            placeholder="Напишите сообщение..."
            class="chat-input"
            rows="3"
        ></textarea>
        <button @click="sendMessage" class="send-button">
          <i class="fa fa-paper-plane"></i>
        </button>
      </div>
    </div>
  </div>
</template>


<script>
import {chatService} from "@/services/apiService";
import SSEManager from "@/services/sseService";


export default {
  data() {
    return {
      messages: [],
      messageText: "",
      user: null,
      chatId: null,
      chatData: null,
      otherUser: null,
      chatName: '',
      isChatOpen: true,
      showGroupTooltip: false,
      isImageUploadModalOpen: false,
      groupImage: null,
      groupImagePreview: null,
    };
  },
  computed: {
    isMouseOverTooltip() {
      return this.showGroupTooltip;
    },
  },
  watch: {
    chatId: {
      immediate: true,
      handler(newChatId, oldChatId) {
        if (oldChatId) {
          SSEManager.disconnect(oldChatId);
        }
        SSEManager.connect(newChatId, this.isChatOpen, this.handleNewMessage);
      },
    },
  },
  mounted() {
    this.isChatOpen = true;
    this.chatId = this.$route.params.chat_id;
    this.fetchChatDetails(this.chatId);
  },
  beforeUnmount() {
    SSEManager.disconnect(this.chatId);
  },
  methods: {
    onGroupMouseLeave() {
      setTimeout(() => {
        if (!this.isMouseOverTooltip) {
          this.showGroupTooltip = false;
        }
      }, 200);
    },

    onTooltipMouseLeave() {
      this.isMouseOverTooltip = false;
      this.showGroupTooltip = false;
    },

    isChatOpenCallback() {
      return this.isChatOpen;
    },

    goBack() {
      this.$router.push('/chats');
    },

    scrollToBottom() {
      this.$nextTick(() => {
        const messagesList = this.$refs.messagesList;
        if (messagesList) {
          messagesList.scrollTop = messagesList.scrollHeight;
        }
      });
    },

    // Fetch chat details including users and messages
    async fetchChatDetails(chatId) {
      try {
        const chatResponse = await this.$store.dispatch("StoreFetchChatDetail", chatId);
        this.user = JSON.parse(localStorage.getItem("user"));
        this.chatData = chatResponse.data;
        this.messages = this.chatData.messages
            .map(message => {
              const message_user = this.chatData.users.find(user => user.id === message.user_id);
              return {
                id: message.message_id,
                user: message_user || {},
                content: message.content,
                created_at: new Date(message.created_at,).toLocaleString(),
                isMine: message.user_id === this.user.id,
              };
            });

        // Set the other user for direct chats
        if (this.chatData.chat_type === "direct") {
          this.otherUser = this.chatData.users.find(user => user.id !== this.user.id);
          this.chatName = `${this.otherUser.first_name} ${this.otherUser.last_name}`;
        }
        this.scrollToBottom();
      } catch (error) {
        console.error("Error fetching chat details:", error);
      }
    },

    handleNewMessage(newMessage) {
      const message_user = this.chatData.users.find(user => user.id === newMessage.user_id);
      const message = {
        id: newMessage.message_id,
        user: message_user || {},
        content: newMessage.content,
        created_at: new Date(newMessage.created_at).toLocaleString(),
        isMine: newMessage.user_id === this.user.id,
      };
      this.messages.push(message);
      this.scrollToBottom();
    },

    openImageUploadModal() {
      this.isImageUploadModalOpen = true;
    },

    closeImageUploadModal() {
      this.isImageUploadModalOpen = false;
      this.resetImageUploadState();
    },

    handleImageUpload(event) {
      const file = event.target.files[0];
      if (file) {
        this.groupImage = file;
        const reader = new FileReader();
        reader.onload = (e) => {
          this.groupImagePreview = e.target.result;
        };
        reader.readAsDataURL(file);
      }
    },

    async uploadGroupImage() {
      if (!this.groupImage) {
        alert("Пожалуйста, выберите изображение для загрузки.");
        return;
      }

      try {
        const formData = new FormData();
        formData.append("uploaded_image", this.groupImage);
        await chatService.updateGroupImage(this.chatData.id, formData);
        alert("Изображение успешно обновлено!");
        this.closeImageUploadModal();
      } catch (error) {
        console.error("Ошибка при загрузке изображения:", error);
        alert("Не удалось загрузить изображение группы. Пожалуйста, попробуйте позже.");
      }
    },

    resetImageUploadState() {
      this.groupImage = null;
      this.groupImagePreview = null;
    },

    // Send message
    async sendMessage() {
      if (this.messageText.trim() === "") return;
      try {
        const messageData = {
          content: this.messageText,
        }
        await chatService.sendMessage(this.chatId, messageData)
        this.messages.push({
          id: Date.now(),
          user: {
            id: this.user.id,
            username: this.user.username,
          },
          content: this.messageText,
          created_at: new Date().toLocaleString(),
          isMine: true,
        });
        this.messageText = "";
        this.scrollToBottom();
      } catch (error) {
        console.error("Error sending message:", error);
      }
    },
  },
};
</script>

<style scoped>
.chat {
  background: linear-gradient(135deg, #73b5e1, #b6d5de);
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  padding: 20px;
}

.chat-container {
  background-color: white;
  padding: 30px 40px;
  border-radius: 15px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 700px;
  height: 80%;
  max-height: 900px;
  display: flex;
  flex-direction: column;
}

.chat-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 30px;
}

.back-button {
  background-color: transparent;
  border: none;
  color: #0078d4;
  font-size: 24px;
  cursor: pointer;
}

.chat-info {
  flex-grow: 1;
  text-align: center;
  font-size: 20px;
  font-weight: bold;
  color: #333;
}

.chat-photo img {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  object-fit: cover;
}

.messages-container {
  flex-grow: 1;
  overflow-y: auto;
  max-height: calc(100vh - 300px);
  padding-right: 10px;
}

.messages-list {
  max-height: 100%;
  overflow-y: scroll;
  padding: 0 15px;
}

.message {
  background-color: #e1f5fe;
  margin: 12px 0;
  padding: 15px 20px;
  border-radius: 12px;
  font-size: 16px;
  color: #333;
}

.message-header {
  display: flex;
  justify-content: space-between;
  font-size: 14px;
  color: #555;
}

.timestamp {
  font-size: 12px;
  color: #888;
}

.message-content {
  margin-top: 10px;
}

.message.mine {
  background-color: #e1e1e1;
}

.message.other {
  background-color: #e1f5fe;
}

.no-messages {
  color: #0078d4;
  font-size: 18px;
  text-align: center;
}

.chat-input-container {
  display: flex;
  justify-content: space-between;
  margin-top: 20px;
}

.chat-input {
  width: 85%;
  padding: 12px 18px;
  font-size: 16px;
  border: 1px solid #ddd;
  border-radius: 12px;
  background-color: #f4f6f9;
  font-family: Arial, sans-serif;
  resize: vertical;
  overflow: hidden;
  white-space: pre-wrap;
  word-wrap: break-word;
}

.send-button {
  width: 10%;
  padding: 8px;
  font-size: 20px;
  background-color: transparent;
  color: #0078d4;
  border: none;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  justify-content: center;
  align-items: center;
}

.group-name {
  position: relative;
  cursor: pointer;
  color: #0078d4;
  text-decoration: underline;
}

.group-tooltip {
  position: absolute;
  top: 100px;
  left: 50%;
  transform: translateX(-50%);
  background: #ffffff;
  border: 1px solid #ddd;
  border-radius: 10px;
  box-shadow: 2px 4px 8px rgba(0, 0, 0, 0.1);
  padding: 20px;
  z-index: 20;
  width: 400px;
}

.group-tooltip h4 {
  margin-bottom: 10px;
  font-size: 16px;
  color: #333;
}

.group-tooltip ul {
  list-style: none;
  padding: 0;
  margin: 0;
  max-height: 150px;
  overflow-y: auto;
}

.group-tooltip ul li {
  font-size: 14px;
  padding: 5px 0;
  color: #555;
}

.tooltip-actions {
  margin-top: 15px;
  display: flex;
  gap: 10px;
  justify-content: space-between;
}

.tooltip-button {
  background: #55ace1;
  color: #fff;
  border: none;
  padding: 8px 10px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
}

.tooltip-button:hover {
  background: #005bb5;
}

.tooltip-user {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 5px 0;
}

.user-avatar {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  object-fit: cover;
  border: 1px solid #ddd;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
}

.modal-content {
  background: white;
  padding: 20px;
  border-radius: 8px;
  max-width: 400px;
  width: 100%;
  text-align: center;
}

.image-preview img {
  max-width: 50%;
  height: auto;
  margin-top: 10px;
}

.modal-actions button {
  margin: 5px;
}


.send-button i {
  font-size: 24px;
}

@media (max-width: 600px) {
  .chat-container {
    padding: 20px;
    width: 90%;
  }

  .chat h2 {
    font-size: 18px;
  }

  .message {
    font-size: 14px;
  }

  .chat-input-container {
    flex-direction: column;
    align-items: center;
  }

  .chat-input {
    width: 100%;
    margin-bottom: 10px;
  }

  .send-button {
    width: 100%;
  }
}

</style>

