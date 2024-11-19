<template>
  <div class="chats">
    <div class="chats-container">
      <h2>Чаты</h2>
      <div v-if="isLoading">
        <div class="loading-container">
          <div class="loading-spinner"></div>
          <p class="loading-text">Загрузка...</p>
        </div>
      </div>
    <div v-else-if="chats && chats.length">
      <div class="chat-item" v-for="chat in chats" :key="chat.chat_id">
        <a :href="'/chats/' + chat.id" class="chat-item-link">
          <div class="chat-header">
          <span
              class="chat-type-icon"
              :title="chat.chat_type === 'direct' ? 'Личный чат' : 'Групповой чат'"
          >
              <i :class="chat.chat_type === 'direct' ? 'fas fa-user' : 'fas fa-users'"></i>
          </span>
            <strong>
              <div v-if="getUserAvatarDirect(chat.users)" class="user-avatar">
                <img :src="getUserAvatarDirect(chat.users)" alt="Avatar"/>
              </div>
              <span class="user-name">{{ getFirstLastNames(chat.users) }}</span>
            </strong>
            <span class="timestamp">{{ formatDate(chat.updated_at) }}</span>
          </div>
        </a>
      </div>
    </div>
    <div v-else-if="error">
      <p class="error-message">{{ error }}</p>
    </div>
    <div v-else>
      <p class="no-chats-message">У вас ещё нет чатов. Вы можете создать новый
        чат.</p>
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
      isLoading: true,
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

        const timeout = setTimeout(() => {
          this.error = 'Не удалось загрузить чаты. Пожалуйста, попробуйте позже.';
          this.isLoading = false;
        }, 10000);

        const response = await axios.get('http://0.0.0.0:8000/api/chats', {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });
        clearTimeout(timeout);
        this.chats = response.data.chats.sort((a, b) => new Date(b.updated_at) - new Date(a.updated_at));
        this.isLoading = false;
      } catch (error) {
        this.error = 'Не удалось загрузить чаты. Пожалуйста, попробуйте позже.';
        this.isLoading = false;
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

    getUserAvatarDirect(users) {
      const instanceUser = JSON.parse(localStorage.getItem("user"));
      if (!instanceUser) {
        this.$router.push('/login');
        alert("Пожалуйста, перезайдите в аккаунт");
        return;
      }

      const user = users.find(user => user.username !== instanceUser.email.split("@")[0] && user.username !== instanceUser.username);

      console.log("IMAGE", user.user_image)
      return user ? user.user_image : '';
    },

    getFirstLastNames(users) {
      const instanceUser = JSON.parse(localStorage.getItem("user"));

      if (!instanceUser) {
        this.$router.push('/login');
        alert("Пожалуйста, перезайдите в аккаунт");
        return;
      }

      return users
          .filter(user => user.username !== instanceUser.email.split("@")[0] && user.username !== instanceUser.username)
          .map(user => `${user.first_name} ${user.last_name}`)
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
                Authorization: `
      Bearer ${token}`,
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
  background: linear-gradient(135deg, #73b5e1, #b6d5de);
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  padding: 20px;
}

.chats-container {
  background-color: white;
  padding: 40px;
  border-radius: 15px;
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.15);
  width: 100%;
  max-width: 800px;
  text-align: center;
}

h2 {
  color: #2a8fbe;
  font-size: 28px;
  margin-bottom: 20px;
}

.chat-item {
  margin-bottom: 20px;
  padding: 20px;
  border-radius: 12px;
  background: #f8f9fa;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.chat-item:hover {
  transform: translateY(-5px);
  box-shadow: 0 6px 15px rgba(0, 0, 0, 0.15);
}

.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center; /* Это выравнивает элементы по вертикали */
}

.user-avatar {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  overflow: hidden;
  display: inline-block;
  margin-right: 10px;
}

.user-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.user-name {
  color: #37a5de;
  display: compact;
  justify-content: center;
  padding: 5px 5px 5px;
}

.chat-type-icon {
  font-size: 16px;
  color: #37a5de;
  margin-right: 10px;
}

.timestamp {
  font-size: 14px;
  color: #aaa;
}

.btn-main {
  padding: 12px 25px;
  background-color: #37a5de;
  color: white;
  border: none;
  border-radius: 25px;
  font-size: 16px;
  font-weight: bold;
  cursor: pointer;
  transition: transform 0.3s, background-color 0.3s;
}

.btn-main:hover {
  background-color: #2a8fbe;
  transform: translateY(-2px);
}

.search-container input {
  width: 100%;
  max-width: 350px;
  padding: 12px;
  border: 2px solid #ddd;
  border-radius: 8px;
  font-size: 16px;
  margin-bottom: 10px;
}

.search-container input:focus {
  border-color: #37a5de;
  box-shadow: 0 0 5px rgba(55, 165, 222, 0.5);
}

.no-chats-message,
.no-users-message {
  color: #777;
  font-size: 16px;
  margin-top: 20px;
}

.user-item {
  padding: 10px 15px;
  background-color: #f9f9f9;
  border: 1px solid #e1e1e1;
  border-radius: 8px;
  margin-bottom: 10px;
  cursor: pointer;
  transition: background-color 0.2s, padding-left 0.2s;
}

.user-item:hover {
  background-color: #f1f1f1;
  padding-left: 20px;
}

.no-users-message {
  font-size: 14px;
  color: #aaa;
  margin-top: 10px;
  text-align: center;
}

.chat-item-link {
  display: block;
  text-decoration: none;
  color: inherit;
}

.chat-item-link:hover .chat-item {
  transform: translateY(-5px);
  box-shadow: 0 6px 15px rgba(0, 0, 0, 0.15);
}

.error-message {
  color: #d9534f;
  font-size: 16px;
  margin-top: 20px;
}
</style>
