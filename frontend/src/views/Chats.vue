<template>
  <div class="chats">
    <div class="chats-container">
      <h2>Чаты</h2>
      <div v-if="chats">
        <p>Добро пожаловать в ваши чаты! Здесь будут отображаться ваши сообщения и беседы.</p>
        <router-link to="/chat-room">
          <button class="btn-main">Перейти в чат</button>
        </router-link>
      </div>
      <div v-else>
        <div class="loading-container">
          <div class="loading-spinner"></div>
          <p class="loading-text">Загрузка...</p>
        </div>
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
    };
  },
  mounted() {
    this.fetchChats();
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
  },
};
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
  color: #0078d4;
  font-size: 24px;
  margin-bottom: 20px;
}

.loading-container {
  text-align: center;
}

.loading-spinner {
  border: 4px solid #f3f3f3;
  border-top: 4px solid #0078d4;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 2s linear infinite;
  margin: 20px auto;
}

.loading-text {
  color: #0078d4;
  font-size: 18px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

@media (max-width: 600px) {
  .chats-container {
    padding: 20px;
    width: 100%;
  }

  .chats h2 {
    font-size: 20px;
  }

  .loading-text {
    font-size: 16px;
  }
}
</style>
