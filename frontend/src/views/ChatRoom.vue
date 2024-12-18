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
              {{ chatName }}
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
                        @click.prevent="openNameUpdateModal">Изменить название</button>
                <div>
                  <button class="tooltip-button" @click.prevent="openImageUploadModal">
                    Изменить фото
                  </button>
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
          <template v-if="chatData && chatData.chat_type === 'group'">
            <img v-if="chatImage" :src="chatImage" alt="Group image"/>
            <img v-else src="/default_group_image.png" alt="Group default image"/>
          </template>
          <template v-else-if="chatData && otherUser">
            <a :href="`/profile/${otherUser.id}`">
              <img v-if=chatImage :src=chatImage alt="Profile"/>
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

          <!-- Group messages by date -->
          <div
              v-for="(messages, date) in groupedMessages"
              :key="date"
              class="message-group">

            <!-- Date separator -->
            <div class="date-separator">
              {{ formatDate(date) }}
            </div>

            <!-- Messages for this date -->
            <div
                class="message"
                v-for="message in messages"
                :key="message.id"
                :ref="el => (messageRefs[message.id] = el)"
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
          {{ message.created_at }}
          <i v-if="message.created_at !== message.updated_at"
             class="fa fa-pencil edited-indicator"
             title="Сообщение было изменено"></i>
            </span>
                <div v-if="message.isMine" class="read-status">
                  <i
                      v-if="message.readStatus.includes('read')"
                      :class="{
                        'fa fa-check-double read': message.readStatus.includes('read')
                      }"
                  ></i>
                  <i
                      v-if="!message.readStatus.includes('read') && message.readStatus.includes('delivered')"
                      :class="{
                        'fa fa-check delivered': message.readStatus.includes('delivered')
                      }"
                  ></i>
                </div>
              </div>
              <div class="message-content">
                <span v-if="message.content">{{ message.content }}</span>
                <img
                    v-if="message.file_path && isImage(message.file_path)"
                    :src="message.file_path"
                    class="message-image"
                    alt="Message attachment"
                />
                <video
                    v-if="message.file_path && isVideo(message.file_path)"
                    :src="message.file_path"
                    controls
                    class="message-video"
                ></video>
                <a
                    v-if="message.file_path && !isImage(message.file_path) && !isVideo(message.file_path)"
                    :href="message.file_path"
                    target="_blank"
                    class="message-other-file"
                >
                  <i class="fa fa-file"></i> {{ message.file_name }}
                </a>
              </div>
              <div v-if="message.isMine" class="message-options">
                <button @click="toggleMenu(message.id)" class="menu-button">...</button>
                <div v-if="message.showMenu" class="menu-dropdown">
                  <button v-if="message.message_type === 'text'"
                          @click="openEditModal(message)"
                          class="icon-button-update">
                    <i class="fa fa-pencil"></i>
                  </button>
                  <button @click="openDeleteModal(message)" class="icon-button-delete">
                    <i class="fa fa-trash"></i>
                  </button>
                  <button v-if="chatType === 'group'"
                          @click="openReadStatusModal(message)" class="icon-button-eye">
                    <i class="fa fa-eye"></i>
                  </button>
                </div>
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
        <label class="attachment-button">
          <i class="fa fa-paperclip"></i>
          <input type="file" @change="handleFileUpload" hidden/>
        </label>
        <textarea
            v-model="messageText"
            @keydown.enter="handleEnter"
            @input="onTyping"
            @keyup="onTyping"
            placeholder="Написать сообщение..."
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

      <!-- Group Usage Modals -->
      <div v-if="isNameUpdateModalOpen" class="modal-overlay">
        <div class="modal-content">
          <h2>Введите новое имя чата</h2>
          <form @submit.prevent="updateNameGroup">
            <div class="form-group">
              <input
                  type="text"
                  v-model="newChatName"
                  placeholder="Написать новое имя чата..."
                  class="chat-name-input"
                  required
              />
            </div>
            <div class="modal-actions">
              <button type="submit" class="update-button">Обновить</button>
              <button type="button" @click="closeNameUpdateModal"
                      class="cancel-button">Отмена
              </button>
            </div>
          </form>
        </div>
      </div>
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

      <!-- Read Status Modal -->
      <div v-if="isReadStatusModalVisible" class="modal-overlay"
           @click.self="closeReadStatusModal">
        <div class="modal">
          <h3 class="modal-title">Кто прочитал сообщение?</h3>
          <ul class="read-status-list">
            <li
                v-for="user in chatData.users.filter(user => user.id !== this.user.id)"
                :key="user.id"
                class="read-status-item"
            >
              <span>{{ user.first_name }} {{ user.last_name }}</span>
              <span>
          <i
              :class="{
              'fa fa-check-double read': isMessageReadByUser(user.id, currentMessage),
              'fa fa-check delivered': !isMessageReadByUser(user.id, currentMessage)
            }"
          ></i>
        </span>
            </li>
          </ul>
          <div class="modal-actions">
            <button @click="closeReadStatusModal" class="close-button">
              Закрыть
            </button>
          </div>
        </div>
      </div>

      <!-- Upload attachments Modal -->
      <div v-if="isUploadModalOpen" class="modal-overlay">
        <div class="modal-content">
          <div class="edit-container">
                <textarea
                    v-model="messageText"
                    class="modal-textarea"
                    placeholder="Написать сообщение..."
                ></textarea>
            <button @click="toggleSmallPicker" class="emoji-button">
              <i class="fas fa-smile"></i>
            </button>
            <emoji-picker
                v-if="showSmallPicker"
                @select="addEmoji"
                class="emoji-picker-small"
            />
          </div>
          <div class="upload-content">
            <!-- File Preview -->
            <div v-if="messageFilePreview">
              <img v-if="isImage(messageFileName)" :src="messageFilePreview"
                   alt="Preview" class="file-image-preview"/>
              <video v-if="isVideo(messageFileName)" :src="messageFilePreview" controls
                     class="file-video-preview"></video>
              <span
                  v-if="messageFileName && !isImage(messageFileName) && !isVideo(messageFileName)">{{
                  messageFileName
                }}</span>
            </div>
          </div>
          <div class="modal-actions">
            <button @click="sendMessage">Отправить</button>
            <button @click="closeUploadModal">Отмена</button>
          </div>
        </div>
      </div>

      <!-- Edit Modal -->
      <div v-if="isEditModalVisible" class="modal-overlay"
           @click.self="closeEditModal">
        <div class="modal">
          <h3 class="modal-title">Изменить сообщение</h3>
          <div class="edit-container">
                <textarea
                    v-model="editMessageText"
                    class="edit-textarea"
                    placeholder="Ввести новый текст..."
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
import {chatService, messageService, readStatusService} from "@/services/apiService";
import SSEManager from "@/services/sseService";
import EmojiPicker from "vue3-emoji-picker";
import 'vue3-emoji-picker/css'
import router from "@/router";


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
      chatType: "",
      otherUser: null,
      chatName: '',
      chatImage: "",
      isChatOpen: true,
      showGroupTooltip: false,
      isImageUploadModalOpen: false,
      isNameUpdateModalOpen: false,
      groupImage: null,
      newChatName: '',
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
      lastReadMessageId: null,
      messageRefs: {},
      isReadStatusModalVisible: false,
      currentMessage: null,
      messageFilePath: null,
      messageFileName: null,
      messageFilePreview: null,
      isUploadModalOpen: false,
      fileToUpload: null,
    };
  },
  computed: {
    isMouseOverTooltip() {
      return this.showGroupTooltip;
    },
    groupedMessages() {
      const grouped = {};
      this.messages.forEach((message) => {
        const date = new Date(message.created_at).toLocaleDateString().split('T')[0];
        if (!grouped[date]) {
          grouped[date] = [];
        }
        grouped[date].push(message);
      });
      return grouped;
    },
  },
  watch: {
    chatId: {
      immediate: true,
      handler(newChatId, oldChatId) {
        if (oldChatId) {
          SSEManager.disconnect(oldChatId);
        }
        SSEManager.connect(
            newChatId,
            this.isChatOpen,
            this.handleNewMessage,
            this.typingCallback,
            this.groupCallback,
            this.readStatusCallback,
        );
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
    this.sendReadStatusOnExit();
    SSEManager.disconnect(this.chatId);
  },
  methods: {
    async sendReadStatusOnExit() {
      if (this.lastReadMessageId) {
        const unreadCount = this.messages.length - this.messages.findIndex(
            msg => msg.id === this.lastReadMessageId
        ) - 1;

        await readStatusService.updateReadStatus(this.chatId, {
          last_read_message_id: this.lastReadMessageId,
          count_unread_msg: unreadCount,
        });
      }
    },

    formatDate(date) {
      const options = {day: 'numeric', month: 'long', year: 'numeric',};
      return new Date(date).toLocaleDateString("ru-RU", options);
    },

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

    openReadStatusModal(message) {
      this.currentMessage = message;
      this.isReadStatusModalVisible = true;
      message.showMenu = false;
    },

    closeReadStatusModal() {
      this.isReadStatusModalVisible = false;
      this.currentMessage = null;
    },

    openUploadModal() {
      this.isUploadModalOpen = true;
    },

    closeUploadModal() {
      this.isUploadModalOpen = false;
      this.messageFilePath = null;
      this.messageFilePreview = null;
      this.messageText = '';
    },

    isMessageReadByUser(userId, message) {
      return message.readUsers && message.readUsers.includes(userId);
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
        this.chatType = chatResponse.data.chat_type

        // Set the other user for direct chats
        if (this.chatData.chat_type === "direct") {
          this.otherUser = this.chatData.users.find(user => user.id !== this.user.id);
          this.chatName = `${this.otherUser.first_name} ${this.otherUser.last_name}`;
          this.chatImage = this.otherUser.user_image
        } else {
          this.chatName = this.chatData.name
          this.chatImage = this.chatData.image
        }
        return Promise.resolve();
      } catch (error) {
        if (error.response) {
          const status = error.response.status;
          switch (status) {
            case 403:
              await router.push("/403");
              break;
            case 404:
              await router.push("/404");
              break;
            case 500:
              await router.push("/500");
              break;
          }
        }
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
          size: isInitialLoad ? 100 : 30,
        });
        const newMessages = response.data.items
            .sort((a, b) => new Date(a.created_at) - new Date(b.created_at))
            .map(message => ({
              id: message.id,
              user: this.chatData.users.find(user => user.id === message.user_id) || {},
              content: message.content,
              file_path: message.file_path,
              file_name: message.file_name,
              message_type: message.message_type,
              created_at: new Date(message.created_at).toLocaleString(),
              updated_at: new Date(message.updated_at).toLocaleString(),
              showMenu: false,
              isMine: message.user_id === this.user.id,
              readStatus: [],
              readUsers: [],
            }));

        const currentUserStatus = this.chatData.read_statuses.find(
            status => status.user_id === this.user.id
        );

        if (currentUserStatus) {
          const {last_read_message_id, count_unread_msg} = currentUserStatus;
          const lastReadMessageId = last_read_message_id;
          const countUnreadMessages = count_unread_msg

          if (isInitialLoad) {
            this.messages = [...newMessages];
          } else {
            this.messages = [...newMessages, ...this.messages];
          }
          this.chatData.read_statuses
              .filter(status => status.user_id !== this.user.id)
              .forEach(status => {
                const {last_read_message_id} = status;

                const lastReadIndex = this.messages.findIndex(
                    message => message.id === last_read_message_id
                );

                this.messages.forEach((message, index) => {
                  if (message.isMine) {
                    if (index <= lastReadIndex) {
                      message.readStatus.push('read');
                      message.readUsers.push(status.user_id);
                    } else {
                      message.readStatus.push('delivered');
                    }
                  }
                });
              });
          if (isInitialLoad && lastReadMessageId && countUnreadMessages < 99) {
            await this.$nextTick();
            const targetMessage = this.messageRefs[lastReadMessageId]

            if (targetMessage) {
              const container = this.$refs.messagesList;
              container.scrollTop = targetMessage.offsetTop - container.offsetTop;
            }
          } else if (isInitialLoad && countUnreadMessages > 99) {
            this.scrollToBottom();
            const lastMessageId = this.messages[this.messages.length - 1].id;
            await readStatusService.updateReadStatus(this.chatId, {
              last_read_message_id: lastMessageId,
              count_unread_msg: 0,
            });
          }

          this.cursor = response.data.next_page;
          this.hasMoreMessages = !!this.cursor;
          const container = this.$refs.messagesList;

          if (!isInitialLoad) {
            const currentScrollTop = container.scrollTop;
            const prevHeight = container.scrollHeight;
            container.scrollTop = currentScrollTop;
            await this.$nextTick();
            const newHeight = container.scrollHeight;
            container.scrollTop = newHeight - prevHeight + currentScrollTop;
          }
        }
      } catch (error) {
        console.error("Ошибка загрузки сообщений:", error);
      } finally {
        this.isLoading = false;
      }
    },

    async onScroll() {
      const container = this.$refs.messagesList;
      const scrollTop = container.scrollTop;
      const scrollHeight = container.scrollHeight;
      const clientHeight = container.clientHeight;

      if (scrollTop < 100 && this.hasMoreMessages) {
        await this.loadMessages();
      }

      const visibleMessages = this.messages.filter(message => {
        const messageElement = this.messageRefs[message.id];
        if (!messageElement || !(messageElement instanceof Element)) return false;
        const rect = messageElement.getBoundingClientRect();
        return rect.top >= 0 && rect.bottom <= window.innerHeight;
      });

      if (visibleMessages.length > 0) {
        const lastVisibleMessage = visibleMessages[visibleMessages.length - 1];
        this.lastReadMessageId = lastVisibleMessage.id;
      }

      if (scrollTop + clientHeight >= scrollHeight - 5 && this.lastReadMessageId) {
        await readStatusService.updateReadStatus(this.chatId, {
          last_read_message_id: this.lastReadMessageId,
          count_unread_msg: 0,
        });
      }
    },

    groupCallback(group_data, type_event) {
      if (type_event === "name") {
        this.chatName = group_data.group_name;
      }
      if (type_event === "image") {
        const timestamp = new Date().getTime();
        this.chatImage = `${group_data.image_url}?t=${timestamp}`;
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

    readStatusCallback(read_status_data) {
      if (read_status_data.user_id === this.user.id) return
      const lastReadIndex = this.messages.findIndex(
          message => message.id === read_status_data.last_read_message_id
      );

      this.messages.forEach((message, index) => {
        if (!message.readUsers) {
          message.readUsers = [];
        }
        if (!message.readStatus) {
          message.readStatus = [];
        }
        if (message.isMine && index <= lastReadIndex) {
          if (!message.readStatus.includes('read')) {
            const deliveredIndex = message.readStatus.indexOf('delivered');
            if (deliveredIndex !== -1) {
              message.readStatus.splice(deliveredIndex, 1);
            }
            message.readStatus.push('read');
          }
        }
        if (index <= lastReadIndex) {
          if (!message.readUsers.includes(read_status_data.user_id)) {
            message.readUsers.push(read_status_data.user_id);
          }
          if (message.readUsers.length > 0 && !message.readStatus.includes('read')) {
            message.readStatus.push('read');
          }
        }
      });
    },

    handleNewMessage(newMessage, action) {
      const existingMessageIndex = this.messages.findIndex(message => message.id === newMessage.id);
      if (action === "new" || action === "recover") {
        const message_user = this.chatData.users.find(user => user.id === newMessage.user_id);
        const message = {
          id: newMessage.id,
          user: message_user || {},
          content: newMessage.content,
          file_path: newMessage.file_path,
          file_name: newMessage.file_name,
          message_type: newMessage.message_type,
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

    openNameUpdateModal() {
      this.isNameUpdateModalOpen = true;
    },

    closeNameUpdateModal() {
      this.isNameUpdateModalOpen = false;
      this.newChatName = "";
    },

    openImageUploadModal() {
      this.isImageUploadModalOpen = true;
    },

    closeImageUploadModal() {
      this.isImageUploadModalOpen = false;
      this.groupImage = null;
      this.groupImagePreview = null;
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

    async updateNameGroup() {
      if (!this.newChatName.trim()) {
        return;
      }
      try {
        await chatService.updateChat(this.chatId, this.newChatName)
        this.chatName = this.newChatName
        this.closeNameUpdateModal();
      } catch (error) {
        console.error('Ошибка обновления имени:', error);
        alert('Не удалось обновить имя чата. Попробуйте снова.');
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
      }, 2000);
    },

    handleEnter(event) {
      if (event.shiftKey) {
        return;
      }
      event.preventDefault();
      this.sendMessage();
    },

    isImage(filePath) {
      return /\.(jpg|jpeg|png|gif|webp)$/i.test(filePath);
    },
    isVideo(filePath) {
      return /\.(mp4|webm|avi|mkv)$/i.test(filePath);
    },

    async handleFileUpload(event) {
      const file = event.target.files[0];
      if (!file) return;

      const reader = new FileReader();
      reader.onload = (e) => {
        this.messageFilePreview = e.target.result;
        this.messageFileName = file.name;
        this.fileToUpload = file
      };
      reader.readAsDataURL(file);
      this.openUploadModal()
    },

    removeFile() {
      this.messageFilePath = null;
      this.messageFileName = null;
      this.messageFilePreview = null;
      this.fileToUpload = null
    },

    // Send message
    async sendMessage() {
      if (!this.messageText.trim() && !this.messageFileName) return;
      if (this.fileToUpload) {
        const formData = new FormData();
        formData.append("uploaded_file", this.fileToUpload);
        try {
          const response = await chatService.uploadAttachments(this.chatId, formData);
          this.messageFilePath = response.data.file_path;
          this.messageFileName = response.data.file_name;
        } catch (error) {
          console.error("Ошибка при загрузке файла:", error);
        }
      }

      const messageData = {
        content: this.messageText || null,
        file_path: this.messageFilePath || null,
        file_name: this.messageFileName || null,
        message_type: this.messageFilePath ? "file" : "text",
      };

      try {
        const lastMessageResponse = await messageService.sendMessage(this.chatId, messageData)
        this.messages.push({
          id: lastMessageResponse.data.id,
          user: {
            id: this.user.id,
            username: this.user.username,
          },
          content: this.messageText,
          file_path: this.messageFilePath,
          file_name: this.messageFileName,
          message_type: messageData.message_type,
          created_at: new Date(lastMessageResponse.data.created_at).toLocaleString(),
          updated_at: new Date(lastMessageResponse.data.updated_at).toLocaleString(),
          isMine: true,
          readStatus: ['delivered'],
        });
        this.messageText = "";
        this.removeFile()
        this.closeUploadModal()
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

.delivered {
  color: gray;
  margin-left: 5px;
}

.read {
  color: #8383e8;
  margin-left: 5px;
}

.fa-check-circle-half-o.delivered {
  color: rgba(128, 128, 128, 0.6);
  margin-left: 5px;
}

.fa-check-circle.delivered {
  color: #4f92e8;
  margin-left: 5px;
}

.date-separator {
  text-align: center;
  margin: 10px 0;
  font-size: 14px;
  font-weight: bold;
  color: #888;
  border-top: 1px solid #ddd;
  padding-top: 5px;
}

.message-group {
  margin-bottom: 20px;
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
  white-space: pre-wrap;
}

.file-image-preview {
  max-width: 100%;
  max-height: 150px;
  object-fit: cover;
  border-radius: 5px;
}

.file-video-preview {
  max-width: 100%;
  max-height: 150px;
  object-fit: cover;
  border-radius: 5px;
}

.file-preview span {
  font-size: 14px;
  color: #333;
  margin-top: 5px;
  word-wrap: break-word;
}

.attachment-button {
  position: relative;
  display: inline-block;
  cursor: pointer;
  font-size: 20px;
  margin-right: 8px;
  color: #007bff;
}

.attachment-button input[type="file"] {
  display: none;
}

.message-image {
  max-width: 25%;
  max-height: 25%;
  height: auto;
  margin-top: 4px;
  display: flex;
  justify-content: center;
  margin-left: 35%;
}

.message-video {
  max-width: 25%;
  max-height: 25%;
  margin-top: 4px;
  display: flex;
  justify-content: center;
  margin-left: 35%;
}

.message-other-file {
  max-width: 50%;
  max-height: 50%;
  height: auto;
  margin-top: 4px;
  display: flex;
  justify-content: center;
  margin-left: 35%;
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

.icon-button-eye {
  background: none;
  border: none;
  font-size: 16px;
  cursor: pointer;
  padding: 5px;
  color: #333;
}

.icon-button-eye:hover {
  color: #72a4e3;
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

.read-status-list {
  list-style: none;
  padding: 0;
}

.read-status-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
}

.chat-input-container {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px;
  background: #f9f9f9;
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

.edit-textarea,
.modal-textarea {
  width: 80%;
  height: 90%;
  margin: 15px 30px;
  padding: 10px;
  border: 1px solid #ced4da;
  border-radius: 8px;
  font-size: 14px;
  line-height: 1.4;
  resize: none;
  font-family: Arial, sans-serif;
  box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.1);
}

.edit-textarea, .modal-textarea:focus {
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

.chat-input {
  width: 85%;
  padding: 12px 18px;
  font-size: 16px;
  border: 1px solid #ddd;
  border-radius: 12px;
  background-color: #f4f6f9;
  font-family: Arial, sans-serif;
  resize: none;
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

