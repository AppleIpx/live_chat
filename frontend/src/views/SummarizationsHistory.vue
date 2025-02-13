<template>
  <div class="summarizations">
    <div class="summarizations-container">
      <h2 class="history">Ваши суммаризации</h2>
      <div class="filters">
        <label class="status-label">Статус:</label>
        <select v-model="selectedStatus" class="select-progress"
                @change="fetchSummarizations" required>
          <option value="in_progress">В процессе</option>
          <option value="success">Успешные</option>
          <option value="error">Неудачные</option>
        </select>
      </div>

      <div v-if="summarizations.length" class="summarization-list">
        <div v-for="summarization in summarizations" :key="summarization.id"
             class="summarization-item">
          <div class="summarization-info">
            <a :href="'/summarization-detail/' + summarization.chat_id"
               class="chat-item-link">
              <p><strong>Чат: </strong>
                {{ summarization.chatName || 'Загружается...' }}
              </p>
              <p><strong>Прогресс:</strong> {{ summarization.progress }}%</p>
              <p><strong>Статус:</strong> {{ formatStatus(summarization.status) }}</p>
              <p><strong>Создано:</strong> {{ formatDate(summarization.created_at) }}
              </p>
              <p v-if="summarization.finished_at"><strong>Окончено:</strong>
                {{ formatDate(summarization.finished_at) }}
              </p>
            </a>
          </div>
          <p v-if="summarization.status === 'error'" class="error-message">
            <strong>Ошибка:</strong> {{ summarization.result.error }}</p>
        </div>
      </div>

      <div v-else class="no-summarizations">
        <p>Нет суммаризаций для отображения.</p>
      </div>
    </div>
  </div>
</template>

<script>
import {aiService, chatService} from "@/services/apiService";

export default {
  data() {
    return {
      instanceUser: null,
      summarizations: [],
      selectedStatus: "in_progress",
      chatName: '',
    };
  },
  mounted() {
    this.instanceUser = JSON.parse(localStorage.getItem("user"));
    if (!this.instanceUser) {
      this.$router.push('/login');
      alert("Пожалуйста, перезайдите в аккаунт");
    }
    this.fetchSummarizations();
  },
  methods: {
    formatDate(date) {
      return new Date(date).toLocaleString();
    },
    async fetchSummarizations() {
      try {
        const response = await aiService.fetchSummarizations(this.selectedStatus);
        this.summarizations = response.data;
        await Promise.all(this.summarizations.map(async (summarization) => {
          summarization.chatName = await this.getChatName(summarization.chat_id);
        }));
      } catch (error) {
        alert("Ошибка при загрузке суммаризаций.");
      }
    },
    async getChatName(chatId) {
      const chatRespose = await chatService.fetchChatDetails(chatId);
      if (chatRespose.data.chat_type === 'direct') {
        return this.getFirstLastNames(chatRespose.data.users);
      }
      if (chatRespose.data.chat_type === 'group') {
        return chatRespose.name || 'Групповой чат';
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
    formatStatus(status) {
      switch (status) {
        case 'in_progress':
          return 'Выполняется';
        case 'success':
          return 'Успешно';
        case 'error':
          return 'Неудачно';
        default:
          return status;
      }
    }
  }
};
</script>

<style scoped>
.summarizations {
  background: linear-gradient(135deg, #73b5e1, #b6d5de);
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  padding: 20px;
}

.summarizations-container {
  background-color: white;
  padding: 40px;
  border-radius: 15px;
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.15);
  width: 100%;
  max-width: 800px;
  text-align: center;
}

.history {
  color: #2a8fbe;
  font-size: 28px;
  margin-bottom: 20px;
}

.filters {
  display: flex;
  justify-content: center;
  margin-bottom: 20px;
}

.status-label {
  font-size: 16px;
  font-weight: bold;
  margin-right: 10px;
}

.select-progress {
  padding: 8px 12px;
  font-size: 14px;
  border-radius: 8px;
  border: 1px solid #ccc;
}

.summarization-list {
  margin-top: 20px;
}

.summarization-item {
  background-color: #f9f9f9;
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 15px;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
}

.summarization-info {
  text-align: left;
}

.error-message {
  color: #d9534f;
  font-weight: bold;
}

.chat-item-link {
  display: block;
  text-decoration: none;
  color: inherit;
}

.no-summarizations {
  margin-top: 20px;
  font-size: 16px;
  color: #999;
}
</style>
