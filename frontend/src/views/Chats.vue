<template>
  <div class="chats">
    <div class="chats-container">
      <h2>Чаты</h2>
      <!-- Кнопки создания чатов -->

      <button @click="openSearch('direct')" class="btn-main">Создать личный чат</button>
      <button @click="openSearch('group')" class="btn-main">Создать группу</button>
      <br>

      <!-- Поиск пользователей -->
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

      <!-- Создание группы -->
      <div v-if="isCreatingGroup" class="group-creation-container">
        <input
            v-model="groupName"
            type="text"
            placeholder="Название группы..."
        />
        <div class="group-image-upload">
          <input type="file" @change="handleImageUpload"/>
          <div v-if="groupImagePreview" class="image-preview">
            <img :src="groupImagePreview" alt="Preview"/>
          </div>
        </div>
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

      <!-- Список чатов -->
      <div v-if="isLoading">
        <div class="loading-container">
          <div class="loading-spinner"></div>
          <p class="loading-text">Загрузка...</p>
        </div>
      </div>
      <div v-else-if="chats && chats.length">
        <br>
        <div class="chat-item" v-for="chat in chats" :key="chat.chat_id">
          <a :href="'/chats/' + chat.id" class="chat-item-link">
            <div class="chat-header">
              <span
                  class="chat-type-icon"
                  :title="chat.chat_type === 'direct' ? 'Личный чат' : 'Групповой чат'"
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
            <p class="last-message">{{
                chat.last_message_content || 'Нет сообщений'
              }}</p>
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
      groupImage: null,
      groupImagePreview: null,
    };
  },
  async mounted() {
    await this.fetchChats();
    this.$store.state.chats.forEach((chat) => {
      SSEManager.connect(chat.id, this.isChatOpenCallback);
    });
    await this.fetchUsers()
  },
  methods: {
    isChatOpenCallback() {
      return false;
    },
    async fetchChats() {
      try {
        const timeout = setTimeout(() => {
          this.error = 'Не удалось загрузить чаты. Пожалуйста, попробуйте позже.';
          this.isLoading = false;
        }, 10000);
        const response = await this.$store.dispatch("StoreFetchChats");
        clearTimeout(timeout);
        this.chats = [...response.data.chats.groups, ...response.data.chats.directs];
        console.log("CHATS", this.chats);
        this.chats.sort((a, b) => new Date(b.updated_at) - new Date(a.updated_at));
        this.isLoading = false;
      } catch (error) {
        console.log(error)
        this.error = 'Не удалось загрузить чаты. Пожалуйста, попробуйте позже.';
        this.isLoading = false;
      }
    },

    async fetchUsers() {
      try {
        const response = await userService.fetchUsers()
        this.users = response.data.users.slice(0, 10);
        this.filteredUsers = this.users;
      } catch (error) {
        console.error('Ошибка получения пользователей:', error);
        this.error = 'Не удалось загрузить пользователей.';
      }
    },

    getChatPhoto(chat) {
      if (chat.chat_type === 'direct') {
        const instanceUser = JSON.parse(localStorage.getItem("user"));
        if (!instanceUser) {
          this.$router.push('/login');
          alert("Пожалуйста, перезайдите в аккаунт");
          return;
        }
        const user = chat.users.find(user => user.username !== instanceUser.email.split("@")[0] && user.username !== instanceUser.username);
        return user ? user.user_image : '';
      }
      if (chat.chat_type === 'group') {
        return chat.image_group
      }
    },

    getChatName(chat) {
      if (chat.chat_type === 'direct') {
        return this.getFirstLastNames(chat.users)
      }
      if (chat.chat_type === 'group') {
        return chat.name_group || 'Групповой чат';
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
      } catch (error) {
        console.error('Ошибка при создании чата:', error);
        alert('Не удалось создать чат. Пожалуйста, попробуйте позже.');
      }
    },

    handleImageUpload(event) {
      const file = event.target.files[0];
      if (file) {
        this.groupImage = file;
        const reader = new FileReader();
        reader.onload = (e) => {
          this.groupImagePreview = e.target.result;
        };
        reader.readAsDataURL(file);
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

        const response = await chatService.createGroupChat(groupData);
        const groupId = response.data.id;
        alert('Группа успешно создана!');
        console.log(this.groupImage)
        if (this.groupImage) {
          await this.updateGroupImage(groupId);
        }

        this.isSearchOpen = false;
        this.groupName = "";
        this.groupImage = null;
        this.groupImagePreview = null;
        this.selectedGroupUsers = [];
      } catch (error) {
        alert('Не удалось создать группу. Пожалуйста, попробуйте позже.');
      }
    },

    async updateGroupImage(groupId) {
      try {
        const formData = new FormData();
        if (this.groupImage) {
          formData.append("uploaded_image", this.groupImage);
        } else {
          console.error("No image selected to upload");
          return;
        }

        await chatService.updateGroupImage(groupId, formData);
      } catch (error) {
        console.error('Error uploading group image:', error);
        alert('Не удалось загрузить изображение группы. Пожалуйста, попробуйте позже.');
      }
    }
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
  display: flex; /* Используем flexbox для центровки */
  justify-content: center; /* Центрируем содержимое по горизонтали */
  align-items: center; /* Центрируем содержимое по вертикали */
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
