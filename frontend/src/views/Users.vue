<template>
  <div class="users-view">
    <h2>Список пользователей</h2>
    <br>
    <div class="search-container">
      <input
          type="text"
          v-model="searchQuery"
          @input="filterUsers"
          placeholder="Поиск по имени пользователя..."
          class="search-input"
      />
    </div>
    <div v-if="users.length" class="users-list">
      <div v-for="user in filteredUsers" :key="user.id" class="user-card">
        <h3>
          <a :href="user.username === currentUser.username ? '/profile/me' : '/profile/' + user.id">
            {{ user.username }}
          </a>
        </h3>
        <i>{{ user.first_name }} {{ user.last_name }}</i>
        <br>
        <a :href="'mailto:' + user.email">{{ user.email }}</a>
      </div>
    </div>
    <div v-else class="no-users">
      <p>Нет пользователей для отображения.</p>
    </div>
  </div>
</template>

<script>
import axios from "axios";

export default {
  data() {
    return {
      users: [],
      filteredUsers: [],
      searchQuery: '',
      currentUser: {},
    };
  },
  async mounted() {
    try {
      const token = localStorage.getItem("accessToken");
      if (!token) {
        this.$router.push("/");
        return;
      }

      const currentUsername = localStorage.getItem("username").split("@")[0];
      this.currentUser = {username: currentUsername};

      const response = await axios.get("http://0.0.0.0:8000/api/users", {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      this.users = response.data.users.filter(user => user.username !== currentUsername);
      this.filteredUsers = this.users;

    } catch (error) {
      console.error("Ошибка при получении списка пользователей:", error);
    }
  },
  methods: {
    filterUsers() {
      const query = this.searchQuery.toLowerCase();
      this.filteredUsers = this.users.filter(user =>
          user.username.toLowerCase().includes(query)
      );
    },
  },
};
</script>

<style scoped>
.users-view {
  background-color: #f7f7f7;
  padding: 20px;
}

h2 {
  color: #333;
  font-size: 28px;
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
  width: 60%;
  max-width: 400px;
  border-radius: 8px;
  border: 1px solid #ccc;
}

.users-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
  align-items: center;
}

.user-card {
  background-color: #dbe3f3;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  width: 50%;
  max-width: 400px;
  text-align: center;
}

.user-card h3 a {
  color: #0078d4;
  text-decoration: none;
  font-size: 20px;
  font-weight: bold;
}

.user-card p {
  font-size: 16px;
  color: #555;
  margin: 8px 0;
}

.no-users {
  text-align: center;
  font-size: 18px;
  color: #666;
}
</style>
