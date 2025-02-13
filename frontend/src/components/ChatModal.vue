<template>
  <div class="chat-modal">
    <div class="chat-modal-content">
      <h2>Выберите чат</h2>
      <div class="pagination">
        <button class="btn-modal-main" @click="loadPreviousPage" :disabled="!previousCursor"
                v-if="previousCursor">
          <i class="fas fa-arrow-left"></i>
        </button>
        <button class="btn-modal-main" @click="loadNextPage" :disabled="!nextCursor"
                v-if="nextCursor">
          <i class="fas fa-arrow-right"></i>
        </button>
      </div>
      <button class="close-btn" @click="$emit('close')">✖</button>
      <div v-if="isLoading" class="loading">Загрузка...</div>
      <div v-else-if="chats.length">
        <div class="chat-item" v-for="chat in chats" :key="chat.id"
             @click="selectChat(chat)">
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
              </div>
              <span class="chat-name">{{ getChatName(chat) }}</span>
            </strong>
          </div>
          <span class="timestamp">{{ formatDate(chat.updated_at) }}</span>
        </div>
      </div>
      <div v-else>Нет доступных чатов</div>
    </div>
  </div>
</template>

<script>
import {handleError} from "@/utils/errorHandler";

export default {
  data() {
    return {
      isLoading: true,
      currentCursor: null,
      nextCursor: null,
      previousCursor: null,
      instanceUser: null,
      chats: [],
    };
  },
  mounted() {
    this.instanceUser = JSON.parse(localStorage.getItem("user"));
    if (!this.instanceUser) {
      this.$router.push('/login');
      alert("Пожалуйста, перезайдите в аккаунт");
      return;
    }
    this.fetchChats();
  },
  methods: {
    async loadNextPage() {
      if (this.nextCursor) {
        await this.fetchChats(this.nextCursor);
      }
    },

    async loadPreviousPage() {
      if (this.previousCursor) {
        await this.fetchChats(this.previousCursor);
      }
    },
    async fetchChats(pageCursor = null) {
      try {
        const timeout = setTimeout(() => {
          this.error = 'Не удалось загрузить чаты. Пожалуйста, попробуйте позже.';
          this.isLoading = false;
        }, 10000);
        const params = new URLSearchParams();
        if (pageCursor) params.append("cursor", pageCursor);
        for (const [key, value] of Object.entries(this.$route.query)) {
          params.append(key, value);
        }
        params.append("size", "5");
        const response = await this.$store.dispatch("StoreFetchChats", params);
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
    selectChat(chat) {
      this.$emit("select-chat", chat);
    },
    getFirstLastNames(users) {
      return users
          .filter(user => user.username !== this.instanceUser.email.split("@")[0] && user.username !== this.instanceUser.username)
          .map(user => {
            if (user.is_deleted) {
              return 'Удаленный аккаунт';
            }
            if (user.is_banned) {
              return 'Заблокированный аккаунт';
            }
            return `${user.first_name} ${user.last_name}`;
          })
          .join(', ');
    },
    formatDate(date) {
      return new Date(date).toLocaleString();
    },
    getChatName(chat) {
      if (chat.chat_type === 'direct') {
        return this.getFirstLastNames(chat.users)
      }
      if (chat.chat_type === 'group') {
        return chat.name || 'Групповой чат';
      }
    },
    getChatPhoto(chat) {
      if (chat.chat_type === 'direct') {
        const user = chat.users.find(user =>
            user.username !== this.instanceUser.email.split("@")[0] &&
            user.username !== this.instanceUser.username
        );
        if (user.is_deleted) return '/deleted_avatar.png';
        if (user.is_banned) return '/banned_avatar.png';
        return user?.user_image || '/default_avatar.png';
      } else if (chat.chat_type === 'group') {
        return chat.image || '/default_group_image.png';
      }
    }
  }
};
</script>

<style scoped>
.chat-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
}

.chat-modal-content {
  background: white;
  padding: 20px;
  border-radius: 8px;
  position: relative;
}
.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 5px;
  padding-right: 5px;
}

.user-info {
  display: revert;
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
.close-btn {
  position: absolute;
  top: 10px;
  right: 10px;
  border: none;
  background: none;
  font-size: 20px;
  cursor: pointer;
  color:black;
}

.chat-item {
  display: flex;
  align-items: center;
  cursor: pointer;
  padding: 10px;
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

.loading {
  text-align: center;
  padding: 20px;
}
.btn-modal-main {
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

.btn-modal-main:hover {
  background-color: #2a8fbe;
  transform: translateY(-2px);
}
</style>
