<template>
  <div class="chat">
    <div class="chat-container">
      <!-- Chat Header -->
      <div class="chat-header">
        <button @click="goBack" class="back-button">
          <i class="fa fa-arrow-left"></i>
        </button>

        <!-- Chat Info -->
        <div class="chat-info">
          <span v-if="chatData">
            <span
                v-if="chatData.chat_type === 'group'"
                class="group-name"
                @mouseover="showGroupTooltip = true"
                @mouseleave="onGroupMouseLeave"
            >
              {{ chatData.name }}
            </span>
            <div
                v-if="showGroupTooltip"
                class="group-tooltip"
                @mouseover="showGroupTooltip = true"
                @mouseleave="onTooltipMouseLeave"
            >
              <ul>
                <li v-for="user in chatData.users" :key="user.id" class="tooltip-user">
                  <a v-if="user && user.id"
                     :href="user.username === this.user.username ? '/profile/me' : '/profile/' + user.id">
                    <img v-if="user.user_image" :src="user.user_image"
                         alt="User Avatar" class="user-avatar">
                    <img v-else src="/default_avatar.png" alt="Default Avatar"
                         class="user-avatar">
                    {{ user.first_name }} {{ user.last_name }}
                  </a>
                </li>
              </ul>
            </div>
            <span v-if="chatData.chat_type==='direct'">{{ chatName }}</span>
          </span>
        </div>

        <div class="chat-photo">
          <template
              v-if="chatData && chatData.chat_type === 'group'">
            <img v-if="chatData.image" :src="chatData.image" alt="Group image"/>
            <img v-else src="/default_group_image.png" alt="Group default image"/>
          </template>
          <template v-else-if="chatData && otherUser">
            <a :href="`/profile/${otherUser.id}`">
              <img v-if="otherUser.user_image" :src="otherUser.user_image"
                   alt="Profile"/>
              <img v-else src="/default_avatar.png" alt="Default profile"/>
            </a>
          </template>
        </div>
      </div>

      <!-- Messages Section -->
      <div class="messages-container">
        <div
            v-if="messages.length"
            class="messages-list"
            ref="messagesList"
            @scroll="onScroll">
          <div
              class="message"
              v-for="message in messages"
              :key="message.id">
            <div class="message-header">
              <strong>
                <a v-if="message.user || message.user_id"
                   :href="message.user.username === user.username ? '/profile/me' : '/profile/' + message.user.id">
                  {{ message.user.id === user.id ? 'Вы' : message.user.username }}
                </a>
                <span v-else>Загрузка...</span>
              </strong>
              <span class="timestamp">
          {{ message.updated_at }}
          <i v-if="message.created_at !== message.updated_at"
             class="fa fa-pencil edited-indicator"
             title="Сообщение было изменено"></i>
        </span>
            </div>
            <div class="message-content">{{ message.content }}</div>
            <div class="message-options">
              <button @click="toggleMenu(message.id)" class="menu-button">...</button>
              <div v-if="message.showMenu" class="menu-dropdown">
                <button @click="openDeleteModal(message)" class="icon-button-delete">
                  <i class="fa fa-trash"></i>
                </button>
              </div>
            </div>
          </div>
        </div>
        <div v-else>
          <p class="no-messages">Нет сообщений...</p>
        </div>

        <!-- Delete Modal -->
        <div v-if="isDeleteModalVisible" class="modal-overlay"
             @click.self="closeDeleteModal">
          <div class="modal">
            <h3 class="modal-title">Вы уверены, что хотите удалить сообщение
              безвозвратно?</h3>
            <div class="modal-actions">
              <button @click="recoverMessage()" class="confirm-button">
                Восстановить сообщение
              </button>
              <button @click="confirmDelete()" class="cancel-button">
                Удалить навсегда
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>


<script>
import {messageService} from "@/services/apiService";


export default {
  data() {
    return {
      messages: [],
      messageText: "",
      user: null,
      chatId: null,
      chatData: null,
      otherUser: null,
      chatName: '',
      isChatOpen: true,
      showGroupTooltip: false,
      isImageUploadModalOpen: false,
      groupImage: null,
      groupImagePreview: null,
      cursor: null,
      isLoading: false,
      hasMoreMessages: true,
      isEditModalVisible: false,
      editMessage: null,
      editMessageText: "",
      isDeleteModalVisible: false,
      messageToDelete: null,
    };
  },
  computed: {
    isMouseOverTooltip() {
      return this.showGroupTooltip;
    },
  },
  mounted() {
    this.chatId = this.$route.params.chat_id;
    this.fetchChatDetails(this.chatId).then(() => {
      this.loadMessages(true);
    }).catch(error => {
      console.error('Ошибка при загрузке чата:', error);
    });
  },
  methods: {
    onGroupMouseLeave() {
      setTimeout(() => {
        if (!this.isMouseOverTooltip) {
          this.showGroupTooltip = false;
        }
      }, 200);
    },

    onTooltipMouseLeave() {
      this.isMouseOverTooltip = false;
      this.showGroupTooltip = false;
    },

    goBack() {
      this.$router.push('/chats/deleted');
    },

    openDeleteModal(message) {
      this.messageToDelete = message;
      this.isDeleteModalVisible = true;
      message.showMenu = false;
    },

    closeDeleteModal() {
      this.isDeleteModalVisible = false;
      this.messageToDelete = null;
    },

    async recoverMessage() {
      if (!this.messageToDelete) return;

      try {
        await messageService.recoverMessage(this.chatId, this.messageToDelete.id);
        this.messages = this.messages.filter(msg => msg.id !== this.messageToDelete.id);
        this.closeDeleteModal();
        if (this.messages.length === 0) {
          this.goBack();
        }
      } catch (error) {
        console.error("Ошибка при восстановлении сообщения", error);
        this.closeDeleteModal();
      }
    },

    async confirmDelete() {
      if (!this.messageToDelete) return;

      try {
        await messageService.deleteMessage(this.chatId, this.messageToDelete.id);
        this.messages = this.messages.filter(msg => msg.id !== this.messageToDelete.id);
        this.closeDeleteModal();
        if (this.messages.length === 0) {
          this.goBack();
        }
      } catch (error) {
        console.error("Ошибка при удалении сообщения", error);
        this.closeDeleteModal();
      }
    },

    scrollToBottom() {
      this.$nextTick(() => {
        const messagesList = this.$refs.messagesList;
        if (messagesList) {
          messagesList.scrollTop = messagesList.scrollHeight;
        }
      });
    },

    // Fetch chat details including users and messages
    async fetchChatDetails(chatId) {
      try {
        const chatResponse = await this.$store.dispatch("StoreFetchChatDetail", chatId);
        this.user = JSON.parse(localStorage.getItem("user"));
        this.chatData = chatResponse.data;

        // Set the other user for direct chats
        if (this.chatData.chat_type === "direct") {
          this.otherUser = this.chatData.users.find(user => user.id !== this.user.id);
          this.chatName = `${this.otherUser.first_name} ${this.otherUser.last_name}`;
        }
        return Promise.resolve();
      } catch (error) {
        console.error("Error fetching chat details:", error);
        return Promise.reject(error);
      }
    },

    toggleMenu(messageId) {
      this.messages.forEach(msg => {
        if (msg.id === messageId) {
          msg.showMenu = !msg.showMenu;
        } else {
          msg.showMenu = false;
        }
      });
    },

    async loadMessages(isInitialLoad = false) {
      if (this.isLoading || (!this.hasMoreMessages && !isInitialLoad)) return;

      this.isLoading = true;

      try {
        const response = await messageService.fetchDeletedMessages(this.chatId, {
          cursor: isInitialLoad ? null : this.cursor,
          size: 30,
        });
        const newMessages = response.data.items
            .sort((a, b) => new Date(a.created_at) - new Date(b.created_at))
            .map(message => ({
              id: message.id,
              user: this.chatData.users.find(user => user.id === message.user_id) || {},
              content: message.content,
              created_at: new Date(message.created_at).toLocaleString(),
              updated_at: new Date(message.updated_at).toLocaleString(),
              showMenu: false,
            }));

        if (isInitialLoad) {
          this.messages = [...newMessages];
        } else {
          this.messages = [...newMessages, ...this.messages];
        }

        this.cursor = response.data.next_page;
        this.hasMoreMessages = !!this.cursor;
        const container = this.$refs.messagesList;

        if (isInitialLoad) {
          this.scrollToBottom();
        } else {
          const currentScrollTop = container.scrollTop;
          const prevHeight = container.scrollHeight;
          container.scrollTop = currentScrollTop;
          await this.$nextTick();
          const newHeight = container.scrollHeight;
          container.scrollTop = newHeight - prevHeight + currentScrollTop;
        }

      } catch (error) {
        console.error("Ошибка загрузки сообщений:", error);
      } finally {
        this.isLoading = false;
      }
    },

    async onScroll() {
      const container = this.$refs.messagesList;
      if (container.scrollTop < 100 && this.hasMoreMessages) {
        await this.loadMessages();
      }
    },
  },
};
</script>

<style scoped>
.chat {
  background: linear-gradient(135deg, #73b5e1, #b6d5de);
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  padding: 20px;
}

.chat-container {
  background-color: white;
  padding: 30px 40px;
  border-radius: 15px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 700px;
  height: 80%;
  max-height: 900px;
  display: flex;
  flex-direction: column;
}

.chat-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 30px;
}

.back-button {
  background-color: transparent;
  border: none;
  color: #0078d4;
  font-size: 24px;
  cursor: pointer;
}

.chat-info {
  flex-grow: 1;
  text-align: center;
  font-size: 20px;
  font-weight: bold;
  color: #333;
}

.chat-photo img {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  object-fit: cover;
}

.messages-container {
  flex-grow: 1;
  overflow-y: auto;
  height: 500px;
  max-height: calc(100vh - 300px);
  padding-right: 10px;
}

.messages-list {
  max-height: 100%;
  overflow-y: scroll;
  padding: 0 15px;
}

.message {
  margin: 12px 0;
  padding: 10px 15px;
  border-radius: 10px;
  font-size: 14px;
  color: #333;
  position: relative;
  align-self: flex-end;
  background-color: #e1e1e1;
}

.message-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
  color: #555;
}

.timestamp {
  font-size: 12px;
  color: #888;
}

.edited-indicator {
  margin-left: 5px;
  font-size: 12px;
  color: gray;
}

.message-content {
  margin-top: 8px;
  font-size: 14px;
}

.message-options {
  position: absolute;
  top: 8px;
  right: 10px;
}

.edited-indicator {
  font-size: 0.85em;
  color: gray;
  margin-left: 5px;
}

.menu-button {
  background: none;
  border: none;
  font-size: 1.2em;
  cursor: pointer;
}

.menu-dropdown {
  position: absolute;
  top: 25px;
  right: 0;
  background: white;
  border: 1px solid #ddd;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  z-index: 10;
  padding: 5px;
  border-radius: 5px;
  display: flex;
  flex-direction: row;
  gap: 5px;
}

.icon-button-delete {
  background: none;
  border: none;
  font-size: 16px;
  cursor: pointer;
  padding: 5px;
  color: #333;
}

.icon-button-delete:hover {
  color: #da0707;
}

.menu-button {
  background: none;
  border: none;
  font-size: 1.2em;
  cursor: pointer;
}

.menu-dropdown {
  position: absolute;
  background: white;
  border: 1px solid #ddd;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  z-index: 10;
  padding: 10px;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
}

.modal {
  background: #f8f9fa;
  padding: 25px;
  border-radius: 12px;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
  max-width: 480px;
  width: 100%;
  margin: 20px auto;
  font-family: Arial, sans-serif;
  color: #333;
}

.modal-title {
  font-size: 1.5rem;
  font-weight: bold;
  margin-bottom: 15px;
  text-align: center;
}

.modal-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 20px;
}

.cancel-button {
  padding: 10px 20px;
  font-size: 14px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: background-color 0.3s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.cancel-button {
  background-color: #dc3545;
  color: white;
}

.cancel-button:hover {
  background-color: #c82333;
}

.no-messages {
  color: #0078d4;
  font-size: 18px;
  text-align: center;
}

.group-name {
  position: relative;
  cursor: pointer;
  color: #0078d4;
  text-decoration: underline;
}

.group-tooltip {
  position: absolute;
  top: 100px;
  left: 50%;
  transform: translateX(-50%);
  background: #ffffff;
  border: 1px solid #ddd;
  border-radius: 10px;
  box-shadow: 2px 4px 8px rgba(0, 0, 0, 0.1);
  padding: 20px;
  z-index: 20;
  width: 400px;
}

.group-tooltip h4 {
  margin-bottom: 10px;
  font-size: 16px;
  color: #333;
}

.group-tooltip ul {
  list-style: none;
  padding: 0;
  margin: 0;
  max-height: 150px;
  overflow-y: auto;
}

.group-tooltip ul li {
  font-size: 14px;
  padding: 5px 0;
  color: #555;
}

.tooltip-user {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 5px 0;
}

.user-avatar {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  object-fit: cover;
  border: 1px solid #ddd;
}

.image-preview img {
  max-width: 50%;
  height: auto;
  margin-top: 10px;
}

.modal-actions button {
  margin: 5px;
}


.send-button i {
  font-size: 24px;
}

@media (max-width: 600px) {
  .chat-container {
    padding: 20px;
    width: 90%;
  }

  .chat h2 {
    font-size: 18px;
  }

  .message {
    font-size: 14px;
  }
}

</style>

