<template>
  <div class="chat">
    <div class="chat-container">
      <!-- Chat Header -->
      <div class="chat-header">
        <button @click="goBack" class="back-button">
          <i class="fa fa-arrow-left"></i>
        </button>

        <!-- User Info -->
        <div class="user-info">
          <span v-if="otherUser.id">{{ chatName }}</span>
          <span v-else>Загрузка...</span>
        </div>

        <div class="user-photo">
          <a v-if="otherUser.id" :href="`/profile/${otherUser.id}`">
            <img :src="otherUser.user_image || '/default-avatar.jpg'" alt="Profile"/>
          </a>
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
                  {{
                    message.user.username === user.username ? 'Вы' : chatName
                  }}
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
import {userService} from "@/services/apiService";
import SSEManager from "@/services/sseService";


export default {
  data() {
    return {
      messages: [],
      messageText: "",
      user: null,
      chatId: null,
      chatData: null,
      chatName: '',
      otherUser: {
        first_name: '',
        last_name: '',
        id: '',
        user_image: null,
      },
      otherUserImage: '',
      users: {},
      isChatOpen: true,
    };
  },
  watch: {
    chatId: {
      immediate: true,
      handler(newChatId, oldChatId) {
        if (oldChatId) {
          SSEManager.disconnect(oldChatId);
        }
        SSEManager.connect(newChatId, this.isChatOpenCallback);
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
    isChatOpenCallback(chatId) {
      return chatId === this.chatId && this.isChatOpen;
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
        const chatResponse = await chatService.fetchChatDetails(chatId);
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

        this.users = this.chatData.users.reduce((acc, user) => {
          acc[user.id] = user;
          return acc;
        }, {});
        this.otherUser = this.chatData.users.find(user => user.id !== this.user.id);
        const userResponse = await userService.fetchUserDetails(this.otherUser.id);
        this.otherUser.user_image = userResponse.data.user_image;
        if (!this.otherUser) {
          console.error('Не удалось найти другого пользователя');
        } else {
          this.chatName = `${this.otherUser.first_name} ${this.otherUser.last_name}`;
        }
        this.scrollToBottom();
      } catch (error) {
        console.error("Ошибка получения информации о чате:", error);
      }
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

.user-info {
  flex-grow: 1;
  text-align: center;
  font-size: 20px;
  font-weight: bold;
  color: #333;
}

.user-photo img {
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

