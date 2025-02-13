<template>
  <div class="summarization">
    <div class="summarization-container">
      <h2 class="choose">Выберите чат и период для новой суммаризации</h2>
      <p style="color: #a42d0e">Внимание! Все ранние суммаризации для этого чата будут
        удалены!</p>
      <form class="summarization-form" @submit.prevent="submitSummarization">
        <div class="form-group">
          <label class="choose-label">Выберите чат:</label>
          <button class="btn-sum-main" @click="openChatModal">
            {{ selectedChat ? getChatName(selectedChat) : "Выбрать чат" }}
          </button>
        </div>

        <div class="form-group">
          <label class="choose-label">Выберите период:</label>
          <select class="select-period" v-model="duration" required>
            <option v-for="option in durationOptions" :key="option.value"
                    :value="option.value">
              {{ option.label }}
            </option>
          </select>
        </div>

        <button type="submit" class="btn-sum-main">Начать суммаризацию</button>
      </form>

      <ChatModal v-if="isChatModalOpen" @close="isChatModalOpen = false"
                 @select-chat="setChat"/>
    </div>
  </div>
</template>

<script>
import ChatModal from "@/components/ChatModal.vue";
import {aiService} from "@/services/apiService";

export default {
  components: {ChatModal},
  data() {
    return {
      isChatModalOpen: false,
      instanceUser: null,
      selectedChat: null,
      duration: "day",
      durationOptions: [
        {value: "day", label: "День"},
        {value: "three_days", label: "Три дня"},
        {value: "week", label: "Неделя"},
        {value: "two_weeks", label: "Две недели"},
        {value: "month", label: "Месяц"}
      ],
    };
  },
  mounted() {
    this.instanceUser = JSON.parse(localStorage.getItem("user"));
    if (!this.instanceUser) {
      this.$router.push('/login');
      alert("Пожалуйста, перезайдите в аккаунт");
    }
  },
  methods: {
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
    getChatName(chat) {
      if (chat.chat_type === 'direct') {
        return this.getFirstLastNames(chat.users)
      }
      if (chat.chat_type === 'group') {
        return chat.name || 'Групповой чат';
      }
    },
    openChatModal() {
      this.isChatModalOpen = true;
    },
    setChat(chat) {
      this.selectedChat = chat;
      this.isChatModalOpen = false;
    },
    async submitSummarization() {
      if (!this.selectedChat) {
        return;
      }
      try {
        await aiService.postSummarization(this.selectedChat.id, this.duration);
        this.$router.push('/summarization-detail/' + this.selectedChat.id);
      } catch (error) {
        if (error.response) {
          if (error.response.status === 400 && error.response.data.detail === "No messages found for this time period") {
            alert("Ошибка: В выбранный период нет сообщений для суммаризации.");
          } else if (error.response.status === 503 && error.response.data.detail === "The use of AI is not enabled") {
            alert("Ошибка: Использование ИИ отключено.");
          } else {
            alert("Произошла ошибка при суммаризации: " + error.response.data.detail);
          }
        } else {
          alert("Ошибка сети или сервера. Попробуйте позже.");
        }
      }
    }
  }
};
</script>

<style>
.summarization {
  background: linear-gradient(135deg, #73b5e1, #b6d5de);
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  padding: 20px;
}

.summarization-container {
  background-color: white;
  padding: 40px;
  border-radius: 15px;
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.15);
  width: 100%;
  max-width: 800px;
  text-align: center;
}

.choose {
  color: #2a8fbe;
  font-size: 28px;
  margin-bottom: 20px;
}

.summarization-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
  align-items: center;
  max-width: 400px;
  margin: 0 auto;
  padding: 20px;
  background-color: #f9f9f9;
  border-radius: 10px;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease-in-out;
}

.summarization-form:hover {
  transform: scale(1.02); /* Легкое увеличение при наведении */
}

.form-group {
  width: 100%;
}

.choose-label {
  font-size: 16px;
  font-weight: bold;
  margin-bottom: 8px;
  display: block;
  color: #333;
}

.select-period {
  width: 100%;
  max-width: 320px;
  padding: 12px;
  font-size: 14px;
  border-radius: 8px;
  border: 1px solid #ccc;
  background-color: #fff;
  color: #333;
  transition: border-color 0.3s ease;
}

.select-period:focus {
  border-color: #2a8fbe;
  outline: none;
}

.btn-sum-main {
  width: 100%;
  max-width: 320px;
  padding: 12px;
  font-size: 16px;
  font-weight: bold;
  background-color: #2a8fbe;
  color: #fff;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: background-color 0.3s ease;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.btn-sum-main:hover {
  background-color: #1d6785;
}

.btn-sum-main:focus {
  outline: none;
  box-shadow: 0 0 5px rgba(46, 133, 220, 0.6);
}
</style>
