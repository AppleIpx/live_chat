<template>
  <div class="chat">
    <div class="chat-container">
      <h2>{{ chatName }}</h2>
      <div v-if="messages.length">
        <div class="message" v-for="message in messages" :key="message.id"
             :class="{'mine': message.isMine, 'other': !message.isMine}">
          <div class="message-header">
            <strong>
              <a v-if="message.user && message.user.username"
                 :href="message.user.username === user.username ? '/profile/me' : '/profile/' + message.user.id">
                {{ message.user.username }}
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
      <div class="chat-input-container">
        <input
            v-model="messageText"
            @keydown.enter="sendMessage"
            placeholder="Напишите сообщение..."
            class="chat-input"
        />
        <button @click="sendMessage" class="send-button">
          <i class="fa fa-paper-plane"></i>
        </button>
      </div>
    </div>
  </div>
</template>


<script>
import axios from "axios";

export default {
  data() {
    return {
      socket: null,
      messages: [],
      messageText: "",
      user: "",
      chatId: null,
      chatName: '',
      users: {},
    };
  },
  mounted() {
    const chatId = this.$route.params.chat_id;
    if (!chatId) {
      console.error("chat_id отсутствует.");
      return;
    }
    this.chatId = chatId;
    this.fetchChatName(chatId);
    this.connectToWebSocket(chatId);
  },
  methods: {
    async getUsernameById(userId) {
      if (this.users[userId]) {
        return this.users[userId];
      }
      const token = localStorage.getItem('accessToken');
      if (!token) {
        this.$router.push('/login');
        return;
      }
      try {
        const response = await axios.get(`http://0.0.0.0:8000/api/users/read/${userId}`, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });
        const userData = await response.data;
        this.users[userId] = userData.username;
        return userData.username;
      } catch (error) {
        console.error("Ошибка получения username:", error);
        return "Неизвестный пользователь";
      }
    },
    async fetchChatName(chatId) {
      try {
        const response = await fetch(`http://localhost:8000/api/chats/${chatId}`);
        const chatData = await response.json();
        this.chatName = chatData.name;
      } catch (error) {
        console.error("Ошибка получения информации о чате:", error);
      }
    },
    async connectToWebSocket(chatId) {
      const storedUser = localStorage.getItem("user");
      if (storedUser) {
        this.user = JSON.parse(storedUser);
      } else {
        console.error("Пользователь не найден в localStorage");
        return;
      }
      const wsUrl = `ws://localhost:8000/ws/${this.user.username}/${chatId}`;
      this.socket = new WebSocket(wsUrl);
      console.log(this.socket)
      console.log(storedUser)

      this.socket.onopen = () => {
        console.log(`Подключение к чату с ID ${chatId} установлено`);
      };

      this.socket.onmessage = async (event) => {
        const data = JSON.parse(event.data);
        console.log("Новое сообщение:", data);
        if (data && data.content) {
          console.log(data)
          const username = await this.getUsernameById(data.user_id);
          console.log("USER:", username)
          this.messages.push({
            id: data.id,
            user: {
              id: data.user_id,
              username: username,
            },
            content: data.content,
            created_at: new Date(data.created_at).toLocaleString(),
            isMine: data.user_id === this.user.id,
          });
        }
      };

      this.socket.onerror = (error) => {
        console.error("Ошибка WebSocket:", error);
      };

      this.socket.onclose = () => {
        console.log("Соединение с WebSocket закрыто");
      };
    },
    sendMessage() {
      if (this.messageText.trim() !== "") {
        const messageData = {
          action_type: "message:send",
          content: this.messageText,
          user: {
            id: this.user.id,
            username: this.user.username,
            email: this.user.email,
            first_name: this.user.first_name,
            last_name: this.user.last_name,
            is_active: true,
            is_verified: false,
            is_superuser: false,
          },
          chat: {
            id: this.chatId,
            chat_type: "direct",
          },
        };
        this.messages.push({
          id: Date.now(),
          user: {
            username: this.user.username,
          },
          content: this.messageText,
          created_at: new Date().toLocaleString(),
          isMine: true,
        });
        this.socket.send(JSON.stringify(messageData));
        this.messageText = "";
      }
    },
  },
};
</script>

<style scoped>
.chat {
  background-color: #f7f7f7;
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  padding: 20px;
}

.chat-container {
  background-color: white;
  padding: 30px;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 600px;
}

.chat h2 {
  color: #0078d4;
  font-size: 24px;
  text-align: center;
  margin-bottom: 20px;
}

.message {
  background-color: #e1f5fe;
  margin: 10px 0;
  padding: 10px;
  border-radius: 8px;
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
  font-size: 16px;
  color: #333;
  margin-top: 5px;
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
  padding: 10px;
  font-size: 16px;
  border: 1px solid #ddd;
  border-radius: 8px;
}

.send-button {
  width: 10%;
  padding: 8px;
  font-size: 20px;
  background-color: transparent;
  color: #0078d4;
  border: none;
  border-radius: 20%;
  cursor: pointer;
  display: flex;
  justify-content: center;
  align-items: center;
}

.send-button i {
  font-size: 22px;
}

@media (max-width: 600px) {
  .chat-container {
    padding: 20px;
    width: 100%;
  }

  .chat h2 {
    font-size: 20px;
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
