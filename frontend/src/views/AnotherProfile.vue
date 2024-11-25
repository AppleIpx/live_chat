<template>
  <div class="profile">
    <div class="profile-container">
      <h2>Профиль пользователя</h2>
      <div v-if="user">
        <div class="profile-info">
          <!-- Avatar Display -->
          <div class="avatar-container">
            <div class="avatar-wrapper">
              <img
                  v-if="user.user_image"
                  :src="user.user_image"
                  alt="Аватар"
                  class="avatar-image"
              />
              <div v-else class="avatar-placeholder"></div>
            </div>
          </div>

          <!-- Profile Information -->
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
          <button class="button">Перейти к совместным чатам (не реализовано)</button>
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
import {userService} from "@/services/apiService";

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
        const user_id = this.$route.params.user_id;
        const response = await userService.fetchUserDetails(user_id)
        this.user = response.data;
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
  background: linear-gradient(135deg, #73b5e1, #b6d5de);
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

.profile-info input {
  width: 100%;
  padding: 8px;
  margin: 5px 0;
  border: 1px solid #ddd;
  border-radius: 5px;
  font-size: 16px;
}

.loading-container {
  text-align: center;
}

.loading-spinner {
  border: 4px solid #f3f3f3;
  border-top: 4px solid #37a5de;
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

.avatar-container {
  text-align: center;
  margin-bottom: 20px;
  position: relative;
}

.avatar-wrapper {
  position: relative;
  display: inline-block;
  width: 150px;
  height: 150px;
}

.avatar-image,
.avatar-placeholder {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  object-fit: cover;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
  background-color: #ddd;
  display: flex;
  justify-content: center;
  align-items: center;
}

.avatar-placeholder::after {
  content: ' ';
  display: block;
}

.button {
  padding: 12px 30px;
  background-color: #37a5de;
  color: white;
  font-size: 16px;
  border-radius: 25px;
  cursor: pointer;
  width: 100%;
  text-align: center;
}

.button:hover {
  background-color: #2a8fbe;
}

</style>
