<template>
  <transition name="fade">
    <div
        class="chat-notification"
        v-if="currentNotification"
        @click="navigateToChat"
        :key="currentNotification.chatId"
    >
      <img :src="currentNotification.userAvatar" alt="avatar" class="avatar"/>
      <div class="content">
        <p class="message">
          <strong>{{ currentNotification.userName }}</strong>:
          {{ currentNotification.messageContent }}
        </p>
      </div>
    </div>
  </transition>
</template>

<script>
import axios from "axios";

export default {
  data() {
    return {
      notificationQueue: [],
      currentNotification: null,
      timeout: null,
    };
  },
  computed: {
    latestMessage() {
      return this.$store.getters.latestMessage;
    },
  },
  watch: {
    latestMessage: {
      immediate: true,
      handler(newMessage) {
        if (newMessage) {
          this.addNotificationToQueue(newMessage);
        }
      },
    },
  },
  methods: {
    async addNotificationToQueue(message) {
      try {
        const token = localStorage.getItem("token");
        const response = await axios.get(
            `http://0.0.0.0:8000/api/users/read/${message.user_id}`,
            {
              headers: {Authorization: `Bearer ${token}`},
            }
        );

        const notification = {
          userAvatar: response.data.user_image,
          userName: `${response.data.first_name} ${response.data.last_name}`,
          messageContent: message.content,
          chatId: message.chat_id,
        };

        this.notificationQueue.push(notification);

        if (!this.currentNotification) {
          this.showNextNotification();
        } else {
          // Если пришло новое уведомление, сбрасываем таймер и прерываем старую анимацию
          clearTimeout(this.timeout);
          this.currentNotification = this.notificationQueue.shift();
          this.showNextNotification();
        }
      } catch (error) {
        console.error("Ошибка при загрузке данных пользователя:", error);
      }
    },
    showNextNotification() {
      if (this.notificationQueue.length === 0) {
        this.currentNotification = null;
        return;
      }
      this.currentNotification = this.notificationQueue.shift();
      clearTimeout(this.timeout);
      this.timeout = setTimeout(() => {
        this.currentNotification = null;
      }, 3000);
    },
    navigateToChat() {
      if (this.currentNotification) {
        this.$router.push(`/chats/${this.currentNotification.chatId}`);
      }
      this.currentNotification = null;
      this.showNextNotification();
    },
  },
  beforeUnmount() {
    clearTimeout(this.timeout);
  },
};
</script>

<style scoped>
.chat-notification {
  top: 10%;
  left: 14%;
  transform: translateX(-50%);
  background-color: #ffffff;
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.2);
  border-radius: 12px;
  display: flex;
  align-items: center;
  padding: 15px 20px;
  width: 400px;
  cursor: pointer;
  z-index: 1000;
  position: fixed;
}

.fade-enter-active, .fade-leave-active {
  transition: opacity 0.5s ease;
}

.fade-enter, .fade-leave-to {
  opacity: 0;
}

.avatar {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  overflow: hidden;
  margin-right: 15px;
}

.avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.content {
  flex: 1;
  white-space: nowrap; /* Запрещает перенос текста */
  overflow: hidden; /* Скрывает текст, который выходит за пределы контейнера */
  text-overflow: ellipsis; /* Добавляет многоточие в случае обрезки */
  max-width: calc(100% - 75px); /* Устанавливает максимальную ширину, учитывая размер аватара */
}

.message {
  margin: 0;
  font-size: 16px;
  color: #333;
  line-height: 1.4;
}
</style>
