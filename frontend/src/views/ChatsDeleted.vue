<template>
  <div class="chats">
    <div class="chats-container">

      <!-- Pagination -->
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

      <!-- Chat List -->
      <div v-if="isLoading">
        <div class="loading-container">
          <div class="loading-spinner"></div>
          <p class="loading-text">Загрузка...</p>
        </div>
      </div>
      <div v-else-if="chats && chats.length">
        <br>
        <div class="chat-item" v-for="chat in chats" :key="chat.chat_id">
          <a :href="'/chats/deleted/' + chat.id" class="chat-item-link">
            <div class="chat-header">
              <span
                  class="chat-type-icon"
                  :title="chat.chat_type === 'direct' ? 'Личный чат' : 'Группа'"
              >
                <i :class="chat.chat_type === 'direct' ? 'fas fa-user' : 'fas fa-users'"></i>
              </span>
              <strong>
                <div class="user-info">
                  <div v-if="getChatPhoto(chat)" class="user-avatar">
                    <img :src="getChatPhoto(chat)" alt="Avatar"/>
                  </div>
                  <span class="chat-name">{{ getChatName(chat) }}</span>
                </div>
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
        <p class="no-chats-message">У вас ещё нет чатов с удалёнными сообщениями.</p>
      </div>
    </div>
  </div>
</template>

<script>
import {chatService} from "@/services/apiService";
import {handleError} from "@/utils/errorHandler";

export default {
  data() {
    return {
      chats: null,
      error: null,
      isLoading: true,
      currentCursor: null,
      nextCursor: null,
      previousCursor: null
    };
  },
  async mounted() {
    await this.fetchDeletedChats();
  },
  methods: {
    async fetchDeletedChats(pageCursor = null) {
      try {
        const timeout = setTimeout(() => {
          this.error = 'Не удалось загрузить чаты. Пожалуйста, попробуйте позже.';
          this.isLoading = false;
        }, 10000);
        const response = await chatService.fetchDeletedChats(pageCursor);
        this.nextCursor = response.data.next_page;
        this.previousCursor = response.data.previous_page || null;
        this.chats = response.data.items;
        this.chats.sort((a, b) => new Date(b.updated_at) - new Date(a.updated_at));
        clearTimeout(timeout);
        this.isLoading = false;
      } catch (error) {
        this.error = await handleError(error);
        this.isLoading = false;
      }
    },

    async loadNextPage() {
      if (this.nextCursor) {
        await this.fetchDeletedChats(this.nextCursor);
      }
    },

    async loadPreviousPage() {
      if (this.previousCursor) {
        await this.fetchDeletedChats(this.previousCursor);
      }
    },

    getChatPhoto(chat) {
      const defaultUserImage = '/default_avatar.png';
      const defaultGroupImage = '/default_group_image.png';
      if (chat.chat_type === 'direct') {
        const instanceUser = JSON.parse(localStorage.getItem("user"));
        if (!instanceUser) {
          this.$router.push('/login');
          alert("Пожалуйста, перезайдите в аккаунт");
          return defaultUserImage;
        }
        const user = chat.users.find(user =>
            user.username !== instanceUser.email.split("@")[0] &&
            user.username !== instanceUser.username
        );
        return user?.user_image || defaultUserImage;
      }
      if (chat.chat_type === 'group') {
        return chat.image || defaultGroupImage;
      }
    },

    getChatName(chat) {
      if (chat.chat_type === 'direct') {
        return this.getFirstLastNames(chat.users)
      }
      if (chat.chat_type === 'group') {
        return chat.name || 'Групповой чат';
      }
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
  },
};
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
  display: flex;
  flex-direction: column;
}

.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 15px;
  margin-bottom: 20px;
}

.pagination h2 {
  color: #37a5de;
  font-size: 24px;
  margin-bottom: 20px;
}

.pagination button:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

.pagination button i {
  font-size: 18px;
}

.chat-item:hover {
  transform: translateY(-5px);
  box-shadow: 0 6px 15px rgba(0, 0, 0, 0.15);
}

.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
  padding-right: 10px;
}

.user-info {
  display: flex;
  align-items: center;
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

.chat-name {
  color: #37a5de;
  display: compact;
  justify-content: right;
  padding: 15px 10px 15px;
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
