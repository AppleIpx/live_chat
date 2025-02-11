<template>
  <div class="chats">
    <div class="chats-container">

      <!-- Pagination with arrows on the sides of the chat creation buttons -->
      <div class="pagination">
        <button class="btn-main" @click="loadPreviousPage" :disabled="!previousCursor"
                v-if="previousCursor">
          <i class="fas fa-arrow-left"></i>
        </button>

        <!-- Chat Creation Buttons -->
        <div class="chat-create-buttons">
          <button @click="openSearch('direct')" class="btn-main">Создать личный чат
          </button>
          <button @click="openSearch('group')" class="btn-main">Создать группу</button>
        </div>

        <button class="btn-main" @click="loadNextPage" :disabled="!nextCursor"
                v-if="nextCursor">
          <i class="fas fa-arrow-right"></i>
        </button>
      </div>


      <!-- Creating a direct chat -->
      <div v-if="isCreatingDirect" class="search-container">
        <input
            v-model="searchQuery"
            type="text"
            placeholder="Поиск по имени пользователя..."
            @input="filterUsers"
        />
        <ul v-if="filteredUsers.length" class="user-list">
          <li
              v-for="user in filteredUsers"
              :key="user.id"
              @click="selectUser(user)"
              class="user-item"
          >
            {{ user.username }}
          </li>
        </ul>
        <p v-else class="no-users-message">Пользователь не найден</p>
      </div>

      <!-- Creating a group -->
      <div v-if="isCreatingGroup" class="group-creation-container">
        <input
            v-model="groupName"
            type="text"
            placeholder="Название группы..."
        />
        <div class="user-selection">
          <p>Выберите пользователей:</p>
          <ul>
            <li
                v-for="user in filteredUsers"
                :key="user.id"
                @click="toggleUserSelection(user)"
                :class="{'selected': selectedGroupUsers.includes(user)}"
                class="user-item"
            >
              <div class="user-info">
                <div v-if="user.user_image" class="avatar">
                  <img :src="user.user_image" alt="Avatar"/>
                </div>
                <div v-else class="avatar">
                  <img src="/default_avatar.png" alt="Аватар по умолчанию"/>
                </div>
                <span class="username">{{ user.username }}</span>
              </div>
              <span class="selection-status">
        <i
            :class="selectedGroupUsers.includes(user) ? 'fas fa-check-circle' : 'far fa-circle'"
        ></i>
      </span>
            </li>
          </ul>
        </div>
        <br>
        <button @click="createGroupChat"
                :disabled="selectedGroupUsers.length < 2 || !groupName"
                class="btn-main">
          Создать группу
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
        <div
            class="chat-item"
            v-for="chat in chats"
            :key="chat.chat_id"
            :class="{'unread-chat': chat.read_statuses[0] && chat.read_statuses[0].count_unread_msg > 0}"
        >
          <a :href="'/chats/' + chat.id" class="chat-item-link">
            <div class="chat-header">
              <span
                  class="chat-type-icon"
                  :title="chat.chat_type === 'direct' ? 'Личный чат' : 'Группа'"
              >
                <i :class="chat.chat_type === 'direct' ? 'fas fa-user' : 'fas fa-users'"></i>
              </span>
              <strong>
                <div class="user-info">
                  <div class="profile-avatar-wrapper">
                    <div v-if="getChatPhoto(chat)" class="user-avatar">
                      <img :src="getChatPhoto(chat)" alt="Avatar"/>
                      <img :src="getChatPhoto(chat)" alt="Avatar"/>
                      <div v-if="chat.chat_type==='direct' && isOnline(chat)"
                           class="online-indicator"></div>
                    </div>
                  </div>
                  <span class="chat-name">{{ getChatName(chat) }}</span>
                  <span
                      v-if="chat.read_statuses[0] && chat.read_statuses[0].count_unread_msg > 0"
                      class="unread-badge">
                    {{
                      chat.read_statuses[0].count_unread_msg > 99 ? '99+' : chat.read_statuses[0].count_unread_msg
                    }}
            </span>
                </div>
              </strong>
              <span class="timestamp">{{ formatDate(chat.updated_at) }}</span>
            </div>
            <p v-if="chat.draft_message" class="last-message">
              <span style="color: #b63434;">Черновик:</span> {{ chat.draft_message }}
            </p>
            <p v-else class="last-message">
              {{ chat.last_message_content || "Нет сообщений" }}
            </p>
          </a>
        </div>
      </div>
      <div v-else-if="error">
        <p class="error-message">{{ error }}</p>
      </div>
      <div v-else>
        <p class="no-chats-message">У вас ещё нет чатов. Вы можете создать новый
          чат.</p>
      </div>
    </div>
  </div>
</template>

<script>
import SSEManager from "@/services/sseService";
import {chatService, userService} from "@/services/apiService";
import {handleError} from "@/utils/errorHandler";

export default {
  data() {
    return {
      chats: null,
      error: null,
      users: [],
      filteredUsers: [],
      searchQuery: '',
      isSearchOpen: false,
      isLoading: true,
      selectedUser: null,
      isChatOpen: false,
      isCreatingGroup: false,
      isCreatingDirect: false,
      selectedGroupUsers: [],
      groupName: '',
      lastMessages: {},
      currentCursor: null,
      nextCursor: null,
      previousCursor: null,
      instanceUser: null,
    };
  },
  async mounted() {
    this.instanceUser = JSON.parse(localStorage.getItem("user"));
    if (!this.instanceUser) {
      this.$router.push('/login');
      alert("Пожалуйста, перезайдите в аккаунт");
      return;
    }
    await this.fetchChats();
    this.$store.state.chats.forEach((chat) => {
      SSEManager.connect(chat.id, false);
    });
    await this.fetchUsers()
  },
  methods: {
    isChatOpenCallback() {
      return false;
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
        params.append("size", "3");
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

    isOnline(chat) {
      if (chat.chat_type === 'direct') {
        const user = chat.users.find(user =>
            user.username !== this.instanceUser.email.split("@")[0] &&
            user.username !== this.instanceUser.username
        );
        if (user.is_deleted || user.is_banned) return false;
        const lastOnlineDate = new Date(user.last_online);
        const now = new Date();
        return (now - lastOnlineDate) <= 3 * 60 * 1000;
      }
    },

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

    async fetchUsers() {
      try {
        const response = await userService.fetchUsers(10)
        this.users = response.data.items;
        this.filteredUsers = this.users.filter(user => user.id !== this.instanceUser.id)
      } catch (error) {
        this.error = await handleError(error);
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

    openSearch(chatType) {
      this.isSearchOpen = true;
      this.isCreatingGroup = chatType === 'group';
      this.isCreatingDirect = chatType === 'direct';
      this.selectedGroupUsers = [];
      this.groupName = '';
    },

    filterUsers() {
      if (this.searchQuery) {
        this.filteredUsers = this.users.filter(user =>
            user.username.toLowerCase().includes(this.searchQuery.toLowerCase())
        );
      } else {
        this.filteredUsers = this.users;
      }
    },

    toggleUserSelection(user) {
      if (this.selectedGroupUsers.includes(user)) {
        this.selectedGroupUsers = this.selectedGroupUsers.filter(u => u !== user);
      } else {
        this.selectedGroupUsers.push(user);
      }
    },

    selectUser(user) {
      this.selectedUser = user;
      this.searchQuery = user.username;
      this.isSearchOpen = false;
      this.createChat(user.id);
    },

    async createChat(recipientUserId) {
      try {
        if (!recipientUserId) return;
        const recipientData = {recipient_user_id: recipientUserId}
        const response = await chatService.createChat(recipientData)
        this.chats.push(response.data);
        alert('Чат успешно создан!');
        location.reload();
      } catch (error) {
        if (error.status === 409) {
          alert(`У вас уже есть этот чат.`);
          return
        }
        this.error = await handleError(error);
      }
    },

    async createGroupChat() {
      try {
        if (this.selectedGroupUsers.length < 2 || !this.groupName) return;

        const recipientUserIds = this.selectedGroupUsers.map(user => user.id);

        const groupData = {
          recipient_user_ids: recipientUserIds,
          name_group: this.groupName,
          image_group: null,
        };

        await chatService.createGroupChat(groupData);
        alert('Группа успешно создана!');
        this.isSearchOpen = false;
        this.groupName = "";
        this.selectedGroupUsers = [];
        location.reload();
      } catch (error) {
        this.error = await handleError(error);
      }
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

.chat-create-buttons {
  display: flex;
  gap: 15px;
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

.unread-chat {
  background-color: #f0f8ff;
  border-left: 4px solid #37a5de;
}

.unread-badge {
  display: inline-block;
  background-color: #37a5de;
  color: white;
  border-radius: 50%;
  padding: 4px 8px;
  font-size: 12px;
  font-weight: bold;
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

.profile-avatar-wrapper {
  position: relative;
  display: inline-block;
}

.online-indicator {
  position: absolute;
  bottom: 5px;
  right: 8px;
  width: 12px;
  height: 12px;
  background-color: #007bff;
  border-radius: 50%;
  border: 2px solid white;
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

.search-container input {
  width: 100%;
  max-width: 350px;
  padding: 12px;
  border: 2px solid #ddd;
  border-radius: 8px;
  font-size: 16px;
  margin-bottom: 10px;
}

.search-container input:focus {
  border-color: #37a5de;
  box-shadow: 0 0 5px rgba(55, 165, 222, 0.5);
}

.no-chats-message,
.no-users-message {
  color: #777;
  font-size: 16px;
  margin-top: 20px;
}

.user-list {
  list-style: none;
  padding: 0;
  margin: 10px 0;
}

.user-item {
  padding: 12px 18px;
  background-color: #fff;
  border: 1px solid #ddd;
  border-radius: 10px;
  margin-bottom: 8px;
  cursor: pointer;
  font-size: 16px;
  color: #333;
  display: flex;
  align-items: center;
  transition: all 0.3s ease;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.user-item:hover {
  background-color: #f0f8ff;
  border-color: #37a5de;
  color: #0073e6;
  transform: translateY(-3px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

.user-item .user-avatar-small {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  margin-right: 10px;
  overflow: hidden;
  flex-shrink: 0;
}

.user-item .user-avatar-small img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.user-selection {
  margin-top: 20px;
  background: #f9f9f9;
  border-radius: 8px;
  padding: 10px 15px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.user-selection p {
  margin-bottom: 10px;
  font-size: 16px;
  font-weight: bold;
  color: #333;
}

.user-selection ul {
  list-style: none;
  margin: 0;
  padding: 0;
}

.user-selection .user-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.2s ease;
}

.user-selection .user-item:hover {
  background: #e8f4fd;
}

.user-selection .user-item.selected {
  background: #d1eaff;
  border: 1px solid #80cfff;
}

.user-selection .user-info {
  display: flex;
  align-items: center;
}

.user-selection .avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  overflow: hidden;
  margin-right: 10px;
  background: #ddd;
}

.user-selection .avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.user-selection .username {
  font-size: 14px;
  color: #333;
  font-weight: 500;
}

.user-selection .selection-status {
  font-size: 18px;
  color: #00b300;
}

.user-selection .selection-status .fa-circle {
  color: #aaa;
}

.user-selection .selection-status .fa-check-circle {
  color: #00b300;
}

.no-users-message {
  font-size: 14px;
  color: #bbb;
  text-align: center;
  margin-top: 15px;
}

.group-creation-container {
  background: #f9fbfd;
  border: 1px solid #e3e8ee;
  border-radius: 15px;
  padding: 20px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
  margin-top: 20px;
}

.group-creation-container input {
  width: 100%;
  max-width: 500px;
  padding: 12px 15px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 16px;
  margin-bottom: 15px;
}

.group-creation-container input:focus {
  border-color: #37a5de;
  box-shadow: 0 0 5px rgba(55, 165, 222, 0.5);
}

.selected {
  border-color: #37a5de;
  background-color: #e6f7ff;
  color: #0073e6;
}

.group-image-upload {
  margin: 15px 0;
  text-align: center;
  justify-content: center;
  display: flex;
}

.group-image-upload p {
  font-size: 14px;
  color: #333;
  margin-bottom: 10px;
}

.group-image-upload input {
  padding: 10px 15px;
  border-radius: 8px;
  border: 1px solid #ddd;
  background-color: #f7f9fc;
  font-size: 14px;
  cursor: pointer;
}

.group-image-upload input:focus {
  border-color: #37a5de;
}

.image-preview {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-top: 15px;
  width: 150px;
  height: 150px;
  border: 2px solid #ddd;
  border-radius: 10px;
  overflow: hidden;
  background-color: #f4f4f4;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}

.image-preview img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.no-users-message {
  font-size: 14px;
  color: #aaa;
  margin-top: 10px;
  text-align: center;
}

.chat-item-link {
  display: block;
  text-decoration: none;
  color: inherit;
}

.last-message {
  font-size: 20px;
  color: #8c8787;
  margin-top: 15px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
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
