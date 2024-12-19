<template>
  <div class="profile">
    <div class="profile-container">
      <div v-if="user">
        <h2 class="profile-header">Профиль {{ user.username }}</h2>
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
              <img
                  v-else
                  src="/default_avatar.png"
                  alt="Аватар по умолчанию"
                  class="avatar-image"
              />
            </div>
          </div>

          <!-- Profile Information -->
          <div class="info-item">
            <i class="fa fa-user"></i>
            <strong class="info-value">{{ user.username }}</strong>
          </div>
          <div class="info-item">
            <i class="fa fa-envelope"></i>
            <a :href="'mailto:' + user.email">
              <strong class="info-value">
                {{ user.email }}
              </strong>
            </a>
          </div>
          <div class="info-item">
            <i class="fa fa-id-card"></i>
            <strong class="info-value">{{ user.first_name || 'Не указано' }}
              {{ user.last_name || 'Не указано' }}</strong>
          </div>
          <div class="info-item">
            <i class="fa fa-user-shield"></i>
            <strong class="info-value">{{
                user.is_superuser ? 'Администратор' : 'Пользователь'
              }}</strong>
          </div>
          <div class="info-item">
            <i
                :class="user.is_verified ? 'fa fa-check-circle success-icon' : 'fa fa-times-circle error-icon'"
            ></i>
            <strong class="info-value">
              {{ user.is_verified ? 'Подтвержден' : 'Не подтвержден' }}
            </strong>
          </div>
        </div>

        <!-- Usage Buttons -->
        <div>
          <router-link :to="{ path: '/chats', query: { user_id_exists: user.id } }">
            <button class="button">Перейти к совместным чатам</button>
          </router-link>

          <button
              v-if="user"
              class="button"
              @click="toggleBlackList"
          >
            {{
              user.is_blocked ? "Удалить из чёрного списка" : "Добавить в чёрный список"
            }}
          </button>

          <div v-else>
            <div class="loading-container">
              <div class="loading-spinner"></div>
              <p class="loading-text">Загрузка...</p>
            </div>
          </div>
        </div>
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
import {blackListService, userService} from "@/services/apiService";
import router from "@/router";

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
    async toggleBlackList() {
      const user_id = this.$route.params.user_id;
      try {
        if (this.user.is_blocked) {
          await blackListService.removeFromBlackList(user_id);
          this.user.is_blocked = false;
        } else {
          await blackListService.addToBlackList(user_id);
          this.user.is_blocked = true;
        }
      } catch (error) {
        await this.handleError(error);
      }
    },

    async fetchUserProfile() {
      try {
        const user_id = this.$route.params.user_id;
        const response = await userService.fetchUserDetails(user_id);
        this.user = response.data;
      } catch (error) {
        await this.handleError(error);
      }
    },

    async handleError(error) {
      if (error.response) {
        const status = error.response.status;
        switch (status) {
          case 403:
            await router.push("/403");
            break;
          case 404:
            await router.push("/404");
            break;
          case 500:
            await router.push("/500");
            break;
        }
      }
      console.error("Ошибка:", error);
      this.error = "Произошла ошибка. Пожалуйста, попробуйте позже.";
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
  background-color: #fff;
  padding: 30px;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 600px;
  text-align: center;
}

.profile-header {
  color: #37a5de;
  font-size: 28px;
  margin-bottom: 20px;
}

.profile-info {
  font-size: 16px;
  color: #333;
  margin-top: 20px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
  margin: 10px 0;
  border-bottom: 1px solid #eee;
  padding-bottom: 10px;
  text-align: center;
}

.info-value {
  color: #000;
  font-size: 16px;
}

.success-icon {
  color: #28a745;
}

.error-icon {
  color: #dc3545;
}

.avatar-container {
  text-align: center;
  margin-bottom: 20px;
  position: relative;
}

.avatar-wrapper {
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
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 64px;
  color: #fff;
  background-color: #37a5de;
}

.button {
  margin-top: 20px;
  padding: 12px 30px;
  background-color: #37a5de;
  color: white;
  font-size: 16px;
  border-radius: 25px;
  cursor: pointer;
  width: 100%;
  text-align: center;
  transition: background-color 0.3s ease;
}

.button:hover {
  background-color: #2a8fbe;
}
</style>
