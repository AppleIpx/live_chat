<template>
  <div class="chats">
    <div class="chats-container">
      <h2>Чаты</h2>
      <div v-if="chats && chats.chats.length">
        <div class="chat-item" v-for="chat in chats.chats" :key="chat.chat_id">
          <div class="chat-header">
            <strong>
              <a :href="'/chats/' + chat.chat_id">
                Чат с {{ getUsernames(chat.users) }}
              </a>
            </strong>
            <span class="timestamp">{{ formatDate(chat.created_at) }}</span>
          </div>
          <div class="message-content">Тип: {{ chat.chat_type }}</div>
        </div>
      </div>
      <div v-else-if="error">
        <p class="error-message">{{ error }}</p>
      </div>
      <div v-else>
        <p>У вас еще нет чатов. Вы можете создать новый чат.</p>
      </div>
      <button @click="openSearch" class="btn-main">Создать чат</button>
      <div v-if="isSearchOpen" class="search-container">
        <input
            v-model="searchQuery"
            type="text"
            placeholder="Поиск по имени пользователя..."
            @input="filterUsers"
        />
        <ul v-if="filteredUsers.length" class="user-list">
          <li
              v-for="user in filteredUsers"
              :key="user.id"
              @click="selectUser(user)"
              class="user-item"
          >
            {{ user.username }}
          </li>
        </ul>
        <p v-else class="no-users-message">Пользователь не найден</p>
      </div>

    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      chats: null,
      error: null,
      users: [],
      filteredUsers: [],
      searchQuery: '',
      isSearchOpen: false,
      selectedUser: null,
    };
  },
  mounted() {
    this.fetchChats();
    this.fetchUsers();
  },
  methods: {
    async fetchChats() {
      try {
        const token = localStorage.getItem('accessToken');
        if (!token) {
          this.$router.push('/login');
          return;
        }

        const response = await axios.get('http://0.0.0.0:8000/api/chats', {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        this.chats = response.data;
      } catch (error) {
        console.error('Ошибка получения чатов:', error);
        this.error = 'Не удалось загрузить чаты. Пожалуйста, попробуйте позже.';
      }
    },
    async fetchUsers() {
      try {
        const token = localStorage.getItem('accessToken');
        const response = await axios.get('http://0.0.0.0:8000/api/users', {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        this.users = response.data.users.slice(0, 10);
        this.filteredUsers = this.users;
      } catch (error) {
        console.error('Ошибка получения пользователей:', error);
        this.error = 'Не удалось загрузить пользователей.';
      }
    },
    getUsernames(users) {
      const instanceUsername = localStorage.getItem("username")
      if (!instanceUsername) {
        this.$router.push('/login');
        return;
      }
      console.log(instanceUsername)
      return users
          .filter(user => user.username !== instanceUsername.split("@")[0])
          .map(user => user.username)
          .join(', ');
    },
    formatDate(date) {
      return new Date(date).toLocaleString();
    },
    openSearch() {
      this.isSearchOpen = true;
    },
    filterUsers() {
      if (this.searchQuery) {
        this.filteredUsers = this.users.filter(user =>
            user.username.toLowerCase().includes(this.searchQuery.toLowerCase())
        );
      } else {
        this.filteredUsers = this.users;
      }
    },
    selectUser(user) {
      this.selectedUser = user;
      this.searchQuery = user.username;
      this.isSearchOpen = false;
      this.createChat(user.id);
    },
    async createChat(recipientUserId) {
      try {
        const token = localStorage.getItem('accessToken');
        if (!recipientUserId) return;

        const response = await axios.post(
            'http://0.0.0.0:8000/api/chats/create/direct/',
            {recipient_user_id: recipientUserId},
            {
              headers: {
                Authorization: `Bearer ${token}`,
              },
            }
        );

        this.chats.push(response.data);
        alert('Чат успешно создан!');
      } catch (error) {
        console.error('Ошибка при создании чата:', error);
        alert('Не удалось создать чат. Пожалуйста, попробуйте позже.');
      }
    },
  }
  ,
}
;
</script>

<style scoped>
.chats {
  background-color: #f7f7f7;
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  padding: 20px;
}

.chats-container {
  background-color: white;
  padding: 30px;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 500px;
  text-align: center;
}

.chats h2 {
  color: #37a5de;
  font-size: 24px;
  margin-bottom: 20px;
}

.chat-item {
  margin-bottom: 15px;
  padding: 15px;
  border: 1px solid #e1e1e1;
  border-radius: 8px;
  text-align: left;
}

.chat-header {
  font-weight: bold;
  color: #333;
}

.timestamp {
  color: #aaa;
  font-size: 14px;
  float: right;
}

.message-content {
  color: #555;
  margin-top: 5px;
}

.error-message {
  color: red;
  font-size: 16px;
}

.search-container {
  margin-top: 5%;
  display: flex;
  justify-content: center;
  flex-direction: column;
  align-items: center;
  width: 100%;
  height: 50%;
  margin-bottom: 30px;
}

.search-container input {
  display: flex;
  justify-content: center;
  padding: 10px;
  width: 100%;
  max-width: 350px;
  border: 2px solid #ddd;
  border-radius: 6px;
  font-size: 16px;
  margin-bottom: 6px;
  transition: all 0.2s ease;
}

.search-container input:focus {
  border-color: #37a5de;
  box-shadow: 0 0 5px rgba(55, 165, 222, 0.5);
}

.btn-main {
  padding: 12px 30px;
  display: inline;
  font-size: 16px;
  font-weight: bold;
  text-transform: uppercase;
  color: #fff;
  background-color: #37a5de;
  border: none;
  cursor: pointer;
  border-radius: 25px;
  transition: transform 0.3s ease, background-color 0.3s ease, box-shadow 0.3s ease;
}

.btn-main:hover {
  background-color: #2a8fbe;
  transform: translateY(-4px);
  box-shadow: 0 5px 5px rgba(0, 0, 0, 0.2);
}

.btn-main:active {
  transform: translateY(1px);
}

.user-list {
  list-style: none;
  padding: 0;
  margin-top: 10px;
  max-height: 200px;
  overflow-y: auto;
  width: 100%;
  max-width: 350px;
}

.user-item {
  padding: 12px;
  cursor: pointer;
  background-color: #f7f7f7;
  border: 1px solid #ddd;
  border-radius: 8px;
  margin-bottom: 8px;
  transition: background-color 0.2s ease, padding 0.2s ease;
}

.user-item:hover {
  background-color: #f0f0f0;
  padding-left: 15px;
}

.no-users-message {
  font-size: 14px;
  color: #aaa;
  margin-top: 10px;
  text-align: center;
}
</style>
