<template>
  <div class="users-view">
    <div class="users-container">
      <div v-if="users">
        <h2>Список пользователей</h2>
        <div class="search-container">
          <input
              type="text"
              v-model="searchQuery"
              @input="filterUsers"
              placeholder="Поиск по имени пользователя..."
              class="search-input"
          />
        </div>
        <div v-if="filteredUsers.length" class="users-list">
          <div v-for="user in filteredUsers" :key="user.id" class="user-card">
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
            <h3>
              <a :href="user.username === currentUser.username ? '/profile/me' : '/profile/' + user.id">
                {{ user.username }}
              </a>
            </h3>
            <p><strong>Имя:</strong> {{ user.first_name }}</p>
            <p><strong>Фамилия:</strong> {{ user.last_name }}</p>
            <p><strong>Email:</strong> <a :href="'mailto:' + user.email">{{
                user.email
              }}</a></p>
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
import {userService} from "@/services/apiService";

export default {
  data() {
    return {
      users: [],
      filteredUsers: [],
      searchQuery: "",
      currentUser: {},
    };
  },
  async mounted() {
    try {
      const currentUsername = localStorage.getItem("username").split("@")[0];
      this.currentUser = {username: currentUsername};
      const response = await userService.fetchUsers()
      this.users = response.data.users.filter(
          (user) => user.username !== currentUsername
      );
      this.filteredUsers = this.users;
    } catch (error) {
      console.error("Ошибка при получении списка пользователей:", error);
    }
  },
  methods: {
    filterUsers() {
      const query = this.searchQuery.toLowerCase();
      this.filteredUsers = this.users.filter((user) =>
          user.username.toLowerCase().includes(query)
      );
    },
  },
};
</script>

<style scoped>
.users-view {
  background: linear-gradient(135deg, #73b5e1, #b6d5de);
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
  padding: 20px;
}

.users-container {
  background-color: white;
  padding: 30px;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 600px;
  margin-top: 70px;

}

h2 {
  color: #37a5de;
  font-size: 24px;
  text-align: center;
  margin-bottom: 20px;
}

.search-container {
  text-align: center;
  margin-bottom: 20px;
}

.search-input {
  padding: 10px;
  font-size: 16px;
  width: 80%;
  max-width: 500px;
  border-radius: 8px;
  border: 1px solid #ccc;
}

.users-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.user-card {
  background-color: #ddedf5;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
  text-align: center;
}

.user-card h3 a {
  color: #489ddc;
  text-decoration: none;
  font-size: 20px;
  font-weight: bold;
}

.user-card p {
  font-size: 16px;
  color: #333;
  margin: 10px 0;
}

.avatar-container {
  text-align: center;
  margin-bottom: 10px;
}

.avatar-wrapper {
  width: 80px;
  height: 80px;
  margin: 0 auto;
  border-radius: 50%;
  overflow: hidden;
  background-color: #ddd;
}

.avatar-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 24px;
  color: #777;
  background-color: #ccc;
  border-radius: 50%;
}

</style>
