<template>
  <div class="summarization">
    <div class="summarization-detail-container">
      <button @click="goBack" class="back-button">
        <i class="fa fa-arrow-left"></i>
      </button>
      <div v-if="summarization && summarization.chatName">
        <div class="header">
          <p><strong>Чат: </strong>
            <a :href="'/chats/' + summarization.chat_id" class="chat-item-link">
              {{ summarization.chatName || 'Загружается...' }}
            </a>
          </p>
          <p><strong>Статус:</strong> {{ formatStatus(status) }}</p>
          <div>
            <strong>Прогресс: </strong>
            <transition name="progress-transition">
              <span :key="progress" class="progress-text">{{ progress }}%</span>
            </transition>
            <div class="progress-bar">
              <div :style="{ width: progress + '%' }" class="progress-bar-fill"></div>
            </div>
          </div>
          <p><strong>Начато:</strong> {{ formatDate(summarization.created_at) }}</p>
          <p v-if="summarization.finished_at"><strong>Окончено:</strong>
            {{ formatDate(summarization.finished_at) }}
          </p>
        </div>
        <div class="error-message" v-if="results.error && status==='error'">
          <p>Произошла ошибка при суммаризации: {{ error }}</p>
        </div>
        <div v-else-if="results && status!=='error'" class="result-section">
          <div v-for="(value, key) in results" :key="key" class="result-item">
            <div class="result-date">{{ formatTextDate(key) }}</div>
            <div class="separator"></div>
            <p class="result-text">
              <span>{{ animatedResults[key] }}</span>
            </p>
          </div>
        </div>
        <div v-if="status === 'in_progress'" class="loading-dots">
          <span class="dot"></span>
          <span class="dot"></span>
          <span class="dot"></span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import {aiService, chatService} from "@/services/apiService";
import SSESummarizerManager from "@/services/sseSummarizerService";
import {handleError} from "@/utils/errorHandler";

export default {
  data() {
    return {
      summarization: null,
      progress: 0,
      status: '',
      results: {},
      chatId: this.$route.params.chatId,
      error: null,
      animatedResults: {},
    };
  },
  mounted() {
    this.instanceUser = JSON.parse(localStorage.getItem("user"));
    if (!this.instanceUser) {
      this.$router.push('/login');
      alert("Пожалуйста, перезайдите в аккаунт");
    }
    this.fetchSummarizationDetails();
    SSESummarizerManager.connect_summarize(this.chatId, this.handleSummarizationUpdate);
  },
  methods: {
    async fetchSummarizationDetails() {
      try {
        const response = await aiService.fetchSummarizationDetail(this.chatId);
        this.summarization = response.data;
        this.status = this.summarization.status
        if (this.status === 'error') {
          this.error = this.summarization.result.error
        }
        this.progress = this.summarization.progress
        this.results = this.summarization.result
        this.animatedResults = this.results
        this.summarization.chatName = await this.getChatName(this.chatId);
      } catch (error) {
        await handleError(error);
      }
    },
    async getChatName(chatId) {
      try {
        const chatRespose = await chatService.fetchChatDetails(chatId);
        if (chatRespose.data.chat_type === 'direct') {
          return this.getFirstLastNames(chatRespose.data.users);
        }
        if (chatRespose.data.chat_type === 'group') {
          return chatRespose.name || 'Групповой чат';
        }
      } catch (error) {
        await handleError(error);
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
    formatTextDate(date) {
      return new Date(date).toLocaleDateString('ru-RU', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
      });
    },
    goBack() {
      this.$router.push('/ai/summarization-history');
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
    },
    handleSummarizationUpdate(summarization_data, type_result) {
      if (type_result === "progress_summarization") {
        this.progress = summarization_data.progress;

        if (!summarization_data.result || Object.keys(summarization_data.result).length === 0) {
          console.warn("summarization_data.result пустой!");
          return;
        }

        Object.entries(summarization_data.result).forEach(([date, text]) => {
          if (!this.results[date]) {
            this.results = {...this.results, [date]: text};
            this.animatedResults[date] = "";
            if (this.status === "in_progress") {
              this.animateText(date, text);
            } else {
              this.animatedResults[date] = text;
            }
          } else {
            this.results[date] += text;
            if (this.status === "in_progress") {
              this.animateText(date, text, this.animatedResults[date]);
            } else {
              this.animatedResults[date] = this.results[date];
            }
          }
        });
        if (this.progress === 100) {
          this.status = "success";
        } else {
          this.status = "in_progress";
        }
        this.$forceUpdate()
      } else if (type_result === "failed_summarization") {
        this.status = "error"
        this.error = summarization_data.detail
      }
    },
    animateText(date, text, currentText = "") {
      let index = 0;
      const delay = 30 * 1000 / text.length;

      const addLetter = () => {
        if (index < text.length) {
          this.animatedResults[date] = currentText + text.substring(0, index + 1);
          index++;
          setTimeout(addLetter, delay);
        }
      };
      addLetter();
    },
  }
};
</script>
<style scoped>
.summarization {
  background: linear-gradient(135deg, #73b5e1, #b6d5de);
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  padding: 20px;
}

.summarization-detail-container {
  background-color: white;
  padding: 40px;
  border-radius: 20px;
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 900px;
  text-align: left;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

.header {
  margin-bottom: 25px;
  padding-bottom: 20px;
  border-bottom: 2px solid #e0e0e0;
}

.header p {
  margin: 10px 0;
}

.chat-item-link {
  color: #4a90e2;
  font-weight: bold;
  text-decoration: none;
}

.chat-item-link:hover {
  text-decoration: underline;
}

.result-section {
  margin-top: 30px;
}

.result-section h3 {
  font-size: 26px;
  color: #333;
  margin-bottom: 20px;
}

.result-item {
  margin: 12px 0;
}

.result-item strong {
  font-size: 18px;
  color: #1c76e6;
}

.result-section {
  margin-top: 30px;
}

.result-section h3 {
  font-size: 26px;
  color: #333;
  margin-bottom: 20px;
  text-align: center;
}

.result-item {
  margin-bottom: 20px;
  padding: 15px;
  background: #f9f9f9;
  border-radius: 10px;
  box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
}

.result-date {
  font-size: 18px;
  font-weight: bold;
  color: #1c76e6;
  text-align: center;
}

.separator {
  width: 100%;
  height: 4px;
  background-color: #ddd;
  margin: 8px 0;
}

.result-text {
  color: #555;
  font-size: 16px;
  line-height: 1.5;
  text-align: justify;
}

.progress-bar {
  width: 100%;
  height: 10px;
  background-color: #e0e0e0;
  border-radius: 5px;
  margin-top: 5px;
  overflow: hidden;
}

.progress-bar-fill {
  height: 100%;
  background-color: #4caf50;
  transition: width 0.5s ease-in-out;
}

.progress-transition-enter-active, .progress-transition-leave-active {
  transition: opacity 1s ease;
}

.progress-transition-enter, .progress-transition-leave-to {
  opacity: 0;
}

.progress-text {
  font-weight: bold;
  font-size: 16px;
}

.error-message {
  color: #fff;
  background: #d9534f;
  font-weight: bold;
  padding: 10px 20px;
  border-radius: 5px;
  text-align: center;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s ease-in-out, opacity 0.3s ease-in-out;
}

.error-message:hover {
  transform: scale(1.05);
  opacity: 0.9;
}


.back-button {
  background-color: transparent;
  border: none;
  color: #0078d4;
  font-size: 26px;
  cursor: pointer;
  margin-bottom: 20px;
}

.back-button i {
  margin-right: 10px;
  font-size: 28px;
}

.fade-enter-active, .fade-leave-active {
  transition: opacity 0.5s;
}

.fade-enter, .fade-leave-to {
  opacity: 0;
}

.loading-dots {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-top: 20px;
  gap: 8px;
}

.dot {
  width: 12px;
  height: 12px;
  background-color: black;
  border-radius: 50%;
  animation: bounce 1.5s infinite ease-in-out;
}

.dot:nth-child(1) {
  animation-delay: 0s;
}

.dot:nth-child(2) {
  animation-delay: 0.2s;
}

.dot:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes bounce {
  0%, 80%, 100% {
    transform: scale(0.8);
    opacity: 0.3;
  }
  40% {
    transform: scale(1);
    opacity: 1;
  }
}


@media (max-width: 768px) {
  .summarization-detail-container {
    padding: 20px;
  }

  .header p, .result-section h3 {
    font-size: 18px;
  }

  .result-item strong {
    font-size: 16px;
  }
}
</style>
