<template>
  <div class="profile">
    <div class="profile-container">
      <h2>Ваш профиль</h2>
      <div v-if="user">
        <div class="profile-info">
          <p><strong>Имя пользователя:</strong> {{ user.username }}</p>
          <p><strong>Email:</strong> {{ user.email }}</p>
          <p><strong>Имя:</strong> {{ user.first_name }}</p>
          <p><strong>Фамилия:</strong> {{ user.last_name }}</p>
          <p><strong>Статус:</strong> {{ user.is_active ? 'Активен' : 'Неактивен' }}</p>
          <p><strong>Роль:</strong>
            {{ user.is_superuser ? 'Администратор' : 'Пользователь' }}</p>
          <p><strong>Подтвержден:</strong> {{ user.is_verified ? 'Да' : 'Нет' }}</p>
        </div>
        <br>
        <router-link to="/chats">
          <button class="btn-main">Перейти к чатам</button>
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
      user: null,
      error: null,
    };
  },
  mounted() {
    this.fetchUserProfile();
  },
  methods: {
    async fetchUserProfile() {
      try {
        const token = localStorage.getItem('accessToken');
        if (!token) {
          this.$router.push('/');
          return;
        }

        const response = await axios.get('http://0.0.0.0:8000/api/users/me', {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });
        this.user = response.data;
        localStorage.setItem('user', JSON.stringify(this.user));
      } catch (error) {
        console.error('Ошибка получения профиля:', error);
        this.error = 'Не удалось загрузить профиль. Пожалуйста, попробуйте позже.';
      }
    },
  },
};
</script>

<style scoped>
.profile {
  background-color: #f7f7f7;
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  padding: 20px;
}

.profile-container {
  background-color: white;
  padding: 30px;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 500px;
}

.profile h2 {
  color: #37a5de;
  font-size: 24px;
  text-align: center;
  margin-bottom: 20px;
}

.profile-info {
  font-size: 16px;
  color: #333;
}

.profile-info p {
  margin: 10px 0;
  line-height: 1.6;
}

.profile-info strong {
  color: #37a5de;
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
  color: #37a5de;
  font-size: 18px;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

@media (max-width: 600px) {
  .profile-container {
    padding: 20px;
    width: 100%;
  }

  .profile h2 {
    font-size: 20px;
  }

  .profile-info p {
    font-size: 14px;
  }
}
</style>
