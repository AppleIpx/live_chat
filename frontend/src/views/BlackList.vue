<template>
  <div class="users-view">
    <div class="users-container">
      <div class="pagination">
        <button class="btn-main" @click="loadPreviousPage" :disabled="!previousCursor"
                v-if="previousCursor">
          <i class="fas fa-arrow-left"></i>
        </button>
        <button class="btn-main" @click="loadNextPage" :disabled="!nextCursor"
                v-if="nextCursor">
          <i class="fas fa-arrow-right"></i>
        </button>
      </div>
      <div v-if="black_list">
        <div v-if="black_list.length" class="users-list">
          <h2>Чёрный список</h2>
          <div v-for="user in black_list" :key="user.id" class="user-card">
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
            <h3>
              <a :href="user.username === currentUser.username ? '/profile/me' : '/profile/' + user.id">
                {{ user.username }}
              </a>
            </h3>
            <p>{{ user.last_name }}</p>
            <p>{{ user.first_name }}</p>
          </div>
        </div>
        <div v-else>
          <h2>В вашем чёрном списке пусто</h2>
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
import {blackListService} from "@/services/apiService";
import {handleError} from "@/utils/errorHandler";

export default {
  data() {
    return {
      black_list: null,
      filteredUsers: [],
      searchQuery: "",
      currentUser: {},
      currentCursor: null,
      nextCursor: null,
      previousCursor: null
    };
  },
  async mounted() {
    try {
      const response = await blackListService.fetchBlockedUsers(3)
      this.nextCursor = response.data.next_page;
      this.previousCursor = response.data.previous_page || null;
      this.black_list = response.data.items
    } catch (error) {
      await handleError(error);
    }
  },
  methods: {
    async loadNextPage() {
      if (this.nextCursor) {
        const response = await blackListService.fetchBlockedUsers(3, this.nextCursor);
        this.nextCursor = response.data.next_page;
        this.previousCursor = response.data.previous_page || null;
        this.black_list = response.data.items
      }
    },
    async loadPreviousPage() {
      if (this.previousCursor) {
        const response = await blackListService.fetchBlockedUsers(3, this.previousCursor);
        this.nextCursor = response.data.next_page;
        this.previousCursor = response.data.previous_page || null;
        this.black_list = response.data.items
      }
    }
  }
};
</script>

<style scoped>
.users-view {
  background: linear-gradient(135deg, #73b5e1, #b6d5de);
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  padding: 20px;
}

.users-container {
  background-color: white;
  padding: 40px;
  border-radius: 15px;
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.15);
  width: 100%;
  max-width: 800px;
  text-align: center;
}

h2 {
  color: #37a5de;
  font-size: 24px;
  text-align: center;
  margin-bottom: 20px;
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

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  margin: 10px 0;
  gap: 10px;
}

.pagination button:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

.pagination button i {
  font-size: 18px;
}

</style>
