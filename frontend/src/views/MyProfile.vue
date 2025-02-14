<template>
  <div class="profile">
    <div v-if="user && user.is_warning && showWarning" class="warning-notification">
      <i class="fas fa-exclamation-triangle warning-icon"></i>
       Вы получили предупреждение из-за токсичности.
      Пожалуйста, внесите изменения в ваш аккаунт для избежания блокировки.
      <button class="close-button" @click="closeWarning">
        <i class="fas fa-times"></i>
      </button>
    </div>
    <div class="profile-container">
      <div v-if="user">
        <!-- Profile Info -->
        <div class="profile-info">
          <!-- Avatar -->
          <div class="avatar-container">
            <div class="avatar-wrapper" @mouseenter="hoverAvatar = true"
                 @mouseleave="hoverAvatar = false">
              <img
                  v-if="selectedAvatar"
                  :src="selectedAvatarPreview"
                  alt="Аватар"
                  class="avatar-image"
              />
              <img
                  v-else-if="user.user_image"
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
              <label v-show="hoverAvatar" for="avatar-input" class="edit-icon">
                <i class="fas fa-pen"></i>
              </label>
            </div>
            <input type="file" id="avatar-input" @change="onFileChange" hidden/>
          </div>

          <form @submit.prevent="saveProfile" class="profile-form">
            <label><strong>Логин</strong></label>
            <input v-model="userForm.username" type="text" required/>
            <br>
            <label><strong>Почта</strong></label>
            <input v-model="userForm.email" type="email" required/>
            <br>

            <label><strong>Имя</strong></label>
            <input v-model="userForm.first_name" type="text" required/>
            <br>

            <label><strong>Фамилия</strong></label>
            <input v-model="userForm.last_name" type="text" required/>
            <br>

            <div class="button-container">
              <button type="submit" class="btn-main">Сохранить изменения</button>
              <button
                  type="submit"
                  class="btn-main"
                  @click="toggleUserState"
              >
                {{
                  user.is_deleted ? "Восстановить аккаунт" : "Удалить аккаунт"
                }}
              </button>
            </div>
          </form>
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
import {userService} from "@/services/apiService";
import {handleError} from "@/utils/errorHandler";

export default {
  data() {
    return {
      user: null,
      userForm: {
        username: '',
        email: '',
        first_name: '',
        last_name: '',
      },
      selectedAvatar: null,
      selectedAvatarPreview: null,
      hoverAvatar: false,
      error: null,
      showWarning: true,
    };
  },
  mounted() {
    this.fetchUserProfile();
  },
  methods: {
    async fetchUserProfile() {
      try {
        const response = await userService.fetchUserMe()
        this.user = response.data;
        this.userForm.username = this.user.username;
        this.userForm.email = this.user.email;
        this.userForm.first_name = this.user.first_name;
        this.userForm.last_name = this.user.last_name;
        localStorage.removeItem('user')
        localStorage.setItem('user', JSON.stringify(this.user));
      } catch (error) {
        await handleError(error);
      }
    },
    closeWarning() {
      this.showWarning = false;
    },
    async toggleUserState() {
      try {
        if (this.user.is_deleted) {
          await userService.recoverUserMe();
          this.user.is_deleted = false;
        } else {
          await userService.deleteUserMe();
          this.user.is_deleted = true;
        }
      } catch (error) {
        await handleError(error);
      }
    },

    async saveProfile() {
      const promises = [];

      if (this.selectedAvatar) {
        const fileExtension = this.selectedAvatar.name.split('.').pop().toLowerCase();
        const validExtensions = ['png', 'jpg', 'jpeg'];

        if (!validExtensions.includes(fileExtension)) {
          alert('Неверное расширение файла. Требуются: PNG, JPG, JPEG.');
          return;
        }
        const userImageForm = new FormData();
        userImageForm.append('uploaded_image', this.selectedAvatar);
        promises.push(userService.updateUserImage(userImageForm))
      }

      if (
          this.userForm.email !== this.user.email ||
          this.userForm.username !== this.user.username ||
          this.userForm.first_name !== this.user.first_name ||
          this.userForm.last_name !== this.user.last_name
      ) {
        promises.push(userService.updateUserInfo(this.userForm))
      }

      try {
        await Promise.all(promises);
        this.selectedAvatar = null;
        this.selectedAvatarPreview = null;
        await this.fetchUserProfile();
      } catch (error) {
        await handleError(error);
      }
    },

    onFileChange(event) {
      this.selectedAvatar = event.target.files[0];
      this.selectedAvatarPreview = URL.createObjectURL(this.selectedAvatar);
    },
  },
}
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

.warning-notification {
  position: absolute;
  top: 100px;
  background-color: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
  padding: 10px;
  border-radius: 5px;
  display: flex;
  align-items: center;
  z-index: 1000;
}

.warning-icon {
  margin-right: 5px;
}

.close-button {
  background: none;
  border: none;
  color: #721c24;
  cursor: pointer;
  margin-left: 10px;
  font-size: 16px; /* Немного увеличиваем размер крестика */
}

.close-button:hover {
  color: #c7254e; /* Более темный цвет при наведении */
}

.edit-icon {
  position: absolute;
  bottom: 10px;
  right: 10px;
  width: 40px;
  height: 40px;
  background: rgba(0, 0, 0, 0.6);
  color: #fff;
  border-radius: 50%;
  display: flex;
  justify-content: center;
  align-items: center;
  cursor: pointer;
  font-size: 20px;
  transition: all 0.3s ease;
}

.edit-icon:hover {
  background: #0078d4;
}

.edit-icon i {
  pointer-events: none;
}

.btn-main {
  padding: 12px 30px;
  display: inline-block;
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

.profile-form {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.button-container {
  display: flex;
  justify-content: center;
  margin-top: 20px;
  width: 100%;
}

</style>
