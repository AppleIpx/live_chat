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
              <div class="tooltip-actions">
                <button class="tooltip-button"
                        @click.prevent>Изменить название (заглушка)</button>
                <div>
                  <button class="tooltip-button" @click.prevent="openImageUploadModal">
                    Изменить фото
                  </button>
                  <div v-if="isImageUploadModalOpen" class="modal-overlay">
                    <div class="modal-content">
                      <h2>Загрузить фото группы</h2>
                      <div class="group-image-upload">
                        <input type="file" @change="handleImageUpload"/>
                        <div v-if="groupImagePreview" class="image-preview">
                          <img :src="groupImagePreview" alt="Preview"/>
                        </div>
                      </div>
                      <div class="modal-actions">
                        <button @click="uploadGroupImage">Загрузить</button>
                        <button @click="closeImageUploadModal">Отмена</button>
                      </div>
                    </div>
                  </div>
                </div>
            </div>
            </div>
            <span v-if="chatData.chat_type==='direct'">{{ chatName }}</span>
            <div v-if="typingMessage" class="typing-indicator">
          {{ typingMessage }}
    </div>
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
              :key="message.id"
              :class="{'mine': message.isMine, 'other': !message.isMine}">
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
            <div v-if="message.isMine" class="message-options">
              <button @click="toggleMenu(message.id)" class="menu-button">...</button>
              <div v-if="message.showMenu" class="menu-dropdown">
                <button @click="openEditModal(message)" class="icon-button-update">
                  <i class="fa fa-pencil"></i>
                </button>
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
      </div>

      <!-- Message Input -->
      <div class="chat-input-container">
        <textarea
            v-model="messageText"
            @keydown.enter="sendMessage"
            @input="onTyping"
            @keyup="onTyping"
            placeholder="Напишите сообщение..."
            class="chat-input"
            rows="3"
        ></textarea>
        <button @click="togglePicker" class="emoji-button">
          <i class="fa-regular fa-face-smile"></i>
        </button>
        <EmojiPicker v-if="showPicker" @select="addEmoji" class="emoji-picker"/>
        <button @click="sendMessage" class="send-button">
          <i class="fa fa-paper-plane"></i>
        </button>
      </div>

      <!-- Delete Modal -->
      <div v-if="isDeleteModalVisible" class="modal-overlay"
           @click.self="closeDeleteModal">
        <div class="modal">
          <h3 class="modal-title">Удалить сообщение?</h3>
          <div class="modal-actions">
            <button @click="confirmDelete(false)" class="confirm-button">
              Переместить в <i>"Недавно удалённые"</i>
            </button>
            <button @click="confirmDelete(true)" class="cancel-button">
              Удалить навсегда
            </button>
          </div>
        </div>
      </div>
      <!-- Edit Modal -->
      <div v-if="isEditModalVisible" class="modal-overlay" @click.self="closeEditModal">
        <div class="modal">
          <h3 class="modal-title">Изменить сообщение</h3>
          <div class="edit-container">
                <textarea
                    v-model="editMessageText"
                    class="edit-textarea"
                    placeholder="Введите новый текст"
                ></textarea>
            <button @click="toggleSmallPicker" class="emoji-button">
              <i class="fas fa-smile"></i>
            </button>
            <emoji-picker
                v-if="showSmallPicker"
                @select="addSmallEmoji"
                class="emoji-picker-small"
            />
          </div>
          <div class="modal-actions">
            <button @click="saveMessage" class="save-button">
              <i class="fa fa-check"></i> Сохранить
            </button>
            <button @click="closeEditModal" class="cancel-button">
              <i class="fa fa-times"></i> Отмена
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>


<script>
import {chatService, messageService} from "@/services/apiService";
import SSEManager from "@/services/sseService";
import EmojiPicker from "vue3-emoji-picker";
import 'vue3-emoji-picker/css'


export default {
  components: {EmojiPicker},
  data() {
    return {
      messages: [],
      messageText: "",
      showPicker: false,
      showSmallPicker: false,
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
      typingMessage: "",
      isTyping: false,
    };
  },
  computed: {
    isMouseOverTooltip() {
      return this.showGroupTooltip;
    },
  },
  watch: {
    chatId: {
      immediate: true,
      handler(newChatId, oldChatId) {
        if (oldChatId) {
          SSEManager.disconnect(oldChatId);
        }
        SSEManager.connect(newChatId, this.isChatOpen, this.handleNewMessage, this.typingCallback);
      },
    },
  },
  mounted() {
    this.isChatOpen = true;
    this.chatId = this.$route.params.chat_id;
    this.fetchChatDetails(this.chatId).then(() => {
      this.loadMessages(true);
    }).catch(error => {
      console.error('Ошибка при загрузке чата:', error);
    });
  },
  beforeUnmount() {
    SSEManager.disconnect(this.chatId);
  },
  methods: {
    togglePicker() {
      this.showPicker = !this.showPicker;
    },

    toggleSmallPicker() {
      this.showSmallPicker = !this.showSmallPicker;
    },

    addEmoji(emoji) {
      this.messageText += emoji.i;
    },

    addSmallEmoji(emoji) {
      this.editMessageText += emoji.i;
    },

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

    isChatOpenCallback() {
      return this.isChatOpen;
    },

    goBack() {
      this.$router.push('/chats');
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

    openEditModal(message) {
      this.editMessage = message;
      this.editMessageText = message.content;
      this.isEditModalVisible = true;
      message.showMenu = false;
    },

    closeEditModal() {
      this.isEditModalVisible = false;
      this.editMessage = null;
      this.editMessageText = "";
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

    async confirmDelete(deleteForever) {
      if (!this.messageToDelete) return;

      try {
        await messageService.deleteMessage(this.chatId, this.messageToDelete.id, deleteForever);
        this.messages = this.messages.filter(msg => msg.id !== this.messageToDelete.id);
        this.closeDeleteModal();
      } catch (error) {
        console.error("Ошибка при удалении сообщения", error);
        this.closeDeleteModal();
      }
    },

    async saveMessage() {
      const newText = this.editMessageText.trim();
      if (!newText) return;
      if (newText === this.editMessage.content.trim()) {
        return;
      }
      try {
        const updatedMessage = await messageService.updateMessage(
            this.chatId,
            this.editMessage.id,
            {content: this.editMessageText}
        );
        this.messages = this.messages.map(msg =>
            msg.id === updatedMessage.data.id ? {
              ...msg,
              content: updatedMessage.data.content,
              updated_at: new Date(updatedMessage.data.updated_at).toLocaleString()
            } : msg
        );
        this.closeEditModal();
      } catch (error) {
        console.error("Ошибка при обновлении сообщения", error);
      }
    },

    async loadMessages(isInitialLoad = false) {
      if (this.isLoading || (!this.hasMoreMessages && !isInitialLoad)) return;

      this.isLoading = true;

      try {
        const response = await messageService.fetchMessages(this.chatId, {
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
              isMine: message.user_id === this.user.id,
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

    typingCallback(typing_data) {
      if (typing_data.is_typing === false) {
        this.typingMessage = "";
        return
      }

      if (this.chatData.chat_type === 'group') {
        this.typingMessage = `${typing_data.username} печатает...`;
      } else {
        this.typingMessage = "печатает...";
      }
    },

    handleNewMessage(newMessage, action) {
      const existingMessageIndex = this.messages.findIndex(message => message.id === newMessage.id);
      if (action === "new" || action === "recover") {
        const message_user = this.chatData.users.find(user => user.id === newMessage.user_id);
        const message = {
          id: newMessage.id,
          user: message_user || {},
          content: newMessage.content,
          created_at: new Date(newMessage.created_at).toLocaleString(),
          updated_at: new Date(newMessage.updated_at).toLocaleString(),
          isMine: newMessage.user_id === this.user.id,
        };
        const index = this.messages.findIndex(
            (msg) => new Date(msg.created_at) > new Date(message.created_at)
        );
        this.messages.splice(index === -1 ? this.messages.length : index, 0, message);
        this.scrollToBottom();
      }
      if (action === "update") {
        const message = this.messages[existingMessageIndex];
        message.content = newMessage.content;
        message.updated_at = new Date(newMessage.updated_at).toLocaleString();
      }
      if (action === "delete") {
        this.messages = this.messages.filter(msg => msg.id !== newMessage.id);
      }
    },

    openImageUploadModal() {
      this.isImageUploadModalOpen = true;
    },

    closeImageUploadModal() {
      this.isImageUploadModalOpen = false;
      this.resetImageUploadState();
      location.reload();
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

    async uploadGroupImage() {
      if (!this.groupImage) {
        alert("Пожалуйста, выберите изображение для загрузки.");
        return;
      }

      try {
        const formData = new FormData();
        formData.append("uploaded_image", this.groupImage);
        await chatService.updateGroupImage(this.chatData.id, formData);
        alert("Изображение успешно обновлено!");
        this.closeImageUploadModal();
      } catch (error) {
        console.error("Ошибка при загрузке изображения:", error);
        alert("Не удалось загрузить изображение группы. Пожалуйста, попробуйте позже.");
      }
    },

    resetImageUploadState() {
      this.groupImage = null;
      this.groupImagePreview = null;
    },

    onTyping() {
      if (this.messageText.trim() === "") {
        this.isTyping = false;
        clearTimeout(this.typingTimeout);
        chatService.sendTypingStatus(this.chatId, false);
        return;
      }

      if (!this.isTyping) {
        this.isTyping = true;
        chatService.sendTypingStatus(this.chatId, true);
      }
      clearTimeout(this.typingTimeout);
      this.typingTimeout = setTimeout(() => {
        this.isTyping = false;
        chatService.sendTypingStatus(this.chatId, false);
      }, 1000);
    },

    // Send message
    async sendMessage() {
      this.isTyping = false;
      if (this.messageText.trim() === "") return;
      try {
        const messageData = {
          content: this.messageText,
        }
        await messageService.sendMessage(this.chatId, messageData)
        const lastMessageResponse = await messageService.fetchLastMessage(this.chatId)
        this.messages.push({
          id: lastMessageResponse.data.id,
          user: {
            id: this.user.id,
            username: this.user.username,
          },
          content: this.messageText,
          created_at: new Date(lastMessageResponse.data.created_at).toLocaleString(),
          updated_at: new Date(lastMessageResponse.data.updated_at).toLocaleString(),
          isMine: true,
        });
        this.messageText = "";
        this.scrollToBottom();
      } catch (error) {
        console.error("Error sending message:", error);
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

.typing-indicator {
  font-size: 14px;
  color: #888;
  margin-top: 5px;
  font-style: italic;
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
  background-color: #e1f5fe;
  margin: 12px 0;
  padding: 10px 15px;
  border-radius: 10px;
  font-size: 14px;
  color: #333;
  position: relative;
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

.message.mine {
  align-self: flex-end;
  background-color: #e1e1e1;
}

.message.other {
  align-self: flex-start;
  background-color: #e1f5fe;
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

.icon-button-update {
  background: none;
  border: none;
  font-size: 16px;
  cursor: pointer;
  padding: 5px;
  color: #333;
}

.icon-button-update:hover {
  color: #007bff;
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

.chat-input-container {
  display: flex;
  align-items: center;
  padding: 10px;
  background: #f9f9f9;
}

.chat-input {
  flex-grow: 1;
  border: 1px solid #ccc;
  border-radius: 5px;
  padding: 10px;
  resize: none;
}

.emoji-button {
  background: #f9f9f9;
  color: #007bff;
  font-size: 20px;
  cursor: pointer;
  padding: 5px;
  margin-left: 10px;
  display: flex;
  justify-content: center;
  align-items: center;
}

.emoji-button:active {
  color: #004fa6;
}

.send-button {
  background: #007bff;
  color: white;
  border: none;
  border-radius: 5px;
  padding: 10px;
  margin-left: 10px;
  cursor: pointer;
}

.send-button i {
  font-size: 16px;
}

.send-button:active {
  color: #004fa6;
}

.emoji-picker {
  position: absolute;
  bottom: 55px;
  left: 55%;
  transform: translateX(-55%);
  background-color: white;
  border-radius: 15px;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
  width: 300px;
  max-height: 300px;
  overflow-y: auto;
  z-index: 10;
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

.emoji-picker-small {
  position: absolute;
  left: 52%;
  transform: translateX(-55%);
  background-color: white;
  border-radius: 15px;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
  width: 300px;
  max-height: 300px;
  overflow-y: auto;
  z-index: 10;
}

.edit-container {
  display: flex;
  align-items: center;
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

.edit-textarea {
  width: 80%;
  height: 90%;
  margin: 15px 30px;
  padding: 10px;
  border: 1px solid #ced4da;
  border-radius: 8px;
  font-size: 14px;
  line-height: 1.4;
  resize: none;
  box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.1);
}

.edit-textarea:focus {
  border-color: #007bff;
  outline: none;
  box-shadow: 0 0 4px rgba(0, 123, 255, 0.25);
}

.modal-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 20px;
}

.save-button,
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

.save-button {
  background-color: #28a745;
  color: white;
}

.save-button:hover {
  background-color: #218838;
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

.chat-input-container {
  display: flex;
  justify-content: space-between;
  margin-top: 20px;
}

.chat-input {
  width: 85%;
  padding: 12px 18px;
  font-size: 16px;
  border: 1px solid #ddd;
  border-radius: 12px;
  background-color: #f4f6f9;
  font-family: Arial, sans-serif;
  resize: vertical;
  overflow: hidden;
  white-space: pre-wrap;
  word-wrap: break-word;
}

.send-button {
  width: 10%;
  padding: 8px;
  font-size: 20px;
  background-color: transparent;
  color: #0078d4;
  border: none;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  justify-content: center;
  align-items: center;
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

.tooltip-actions {
  margin-top: 15px;
  display: flex;
  gap: 10px;
  justify-content: space-between;
}

.tooltip-button {
  background: #55ace1;
  color: #fff;
  border: none;
  padding: 8px 10px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
}

.tooltip-button:hover {
  background: #005bb5;
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

.modal-content {
  background: white;
  padding: 20px;
  border-radius: 8px;
  max-width: 400px;
  width: 100%;
  text-align: center;
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

  .chat-input-container {
    flex-direction: column;
    align-items: center;
  }

  .chat-input {
    width: 100%;
    margin-bottom: 10px;
  }

  .send-button {
    width: 100%;
  }
}

</style>

