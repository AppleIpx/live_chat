<template>
  <div class="profile">
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
              <div v-else class="avatar-placeholder"></div>
              <label v-show="hoverAvatar" for="avatar-input" class="edit-icon">
                <i class="fas fa-pen"></i>
              </label>
            </div>
            <input type="file" id="avatar-input" @change="onFileChange" hidden/>
          </div>

          <form @submit.prevent="saveProfile" class="profile-form">
            <label><strong>Username</strong></label>
            <input v-model="userForm.username" type="email" readonly/>
            <br>
            <label><strong>Email</strong></label>
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
import axios from 'axios';

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
    };
  },
  mounted() {
    this.fetchUserProfile();
  },
  methods: {
    async fetchUserProfile() {
      const token = localStorage.getItem('accessToken');
      if (!token) {
        this.$router.push('/');
        return;
      }

      try {
        const response = await axios.get('http://0.0.0.0:8000/api/users/me', {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });
        this.user = response.data;
        this.userForm.username = this.user.username;
        this.userForm.email = this.user.email;
        this.userForm.first_name = this.user.first_name;
        this.userForm.last_name = this.user.last_name;
        localStorage.setItem('user', JSON.stringify(this.user));
        console.log(localStorage.getItem("user"))
      } catch (error) {
        console.error('Ошибка загрузки профиля:', error);
        alert('Не удалось загрузить данные профиля. Попробуйте снова.');
        this.$router.push('/');
      }
    },

    async saveProfile() {
      const token = localStorage.getItem('accessToken');
      if (!token) {
        this.$router.push('/');
        return;
      }
      const promises = [];

      if (this.selectedAvatar) {
        const fileExtension = this.selectedAvatar.name.split('.').pop().toLowerCase();
        const validExtensions = ['png', 'jpg', 'jpeg'];

        if (!validExtensions.includes(fileExtension)) {
          alert('Неверное расширение файла. Требуются: PNG, JPG, JPEG.');
          return;
        }
        const formData = new FormData();
        formData.append('uploaded_image', this.selectedAvatar);
        promises.push(
            axios.patch(
                'http://0.0.0.0:8000/api/users/me/upload-image',
                formData,
                {
                  headers: {
                    Authorization: `Bearer ${token}`,
                    'Content-Type': 'multipart/form-data',
                  },
                }
            )
        );
      }

      if (
          this.userForm.email !== this.user.email ||
          this.userForm.first_name !== this.user.first_name ||
          this.userForm.last_name !== this.user.last_name
      ) {
        promises.push(
            axios.patch(
                'http://0.0.0.0:8000/api/users/me',
                this.userForm,
                {
                  headers: {Authorization: `Bearer ${token}`},
                }
            )
        );
      }

      try {
        await Promise.all(promises);
        await this.fetchUserProfile();
        alert('Профиль успешно обновлен');
        this.selectedAvatar = null;
        this.selectedAvatarPreview = null;

      } catch (error) {
        console.error('Ошибка сохранения профиля:', error);
        alert('Не удалось обновить профиль');
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
