<template>
  <div class="home">
    <div class="welcome-container">
      <h2 v-if="isLoggedIn">Здравствуйте, {{ username }}!</h2>
      <h1 v-else>Добро пожаловать!</h1>
      <p v-if="isLoggedIn">
        Рады видеть вас снова! Перейдите к своим чатам, чтобы продолжить общение.
      </p>
      <p v-else>
        Присоединяйтесь к LiveChat, чтобы общаться с друзьями и коллегами в реальном времени.
        Создайте свой аккаунт или войдите, чтобы начать!
      </p>
      <div class="buttons">
        <router-link v-if="isLoggedIn" to="/chats">
          <button class="btn-main">Перейти к чатам</button>
        </router-link>
        <div v-else class="buttons">
          <router-link to="/login">
            <button class="btn-main">Войти</button>
          </router-link>
          <router-link to="/register">
            <button class="btn-main">Зарегистрироваться</button>
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      isLoggedIn: false,
      username: null,
    };
  },
  mounted() {
    this.checkLoginStatus();
  },
  methods: {
    checkLoginStatus() {
      const token = localStorage.getItem('accessToken');
      if (token) {
        this.isLoggedIn = true;
        this.username = localStorage.getItem('username') || 'пользователь';
      }
    },
  },
};
</script>

<style scoped>
.home {
  background: linear-gradient(135deg, #73b5e1, #b6d5de);
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  padding: 20px;
  overflow: hidden;
}

.welcome-container {
  background: #ffffff;
  padding: 40px;
  border-radius: 16px;
  box-shadow: 0 6px 24px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 600px;
  text-align: center;
  animation: slideIn 0.8s ease-out;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

h1 {
  color: #2d4a6e;
  font-size: 34px;
  margin-bottom: 15px;
  font-weight: bold;
  text-transform: uppercase;
  letter-spacing: 1.2px;
}

h2 {
  color: #3e5a7a;
  font-size: 28px;
  margin-bottom: 10px;
}

p {
  font-size: 18px;
  color: #5b6d81;
  margin-bottom: 25px;
  line-height: 1.5;
}

.buttons {
  display: flex;
  justify-content: center;
  gap: 15px;
}

.btn-main {
  padding: 12px 30px;
  font-size: 16px;
  font-weight: bold;
  text-transform: uppercase;
  color: #fff;
  background-color: #37a5de;
  border: none;
  cursor: pointer;
  border-radius: 25px;
  transition: transform 0.3s ease, background-color 0.3s ease, box-shadow 0.3s ease;
}

.btn-main:hover {
  background-color: #2a8fbe;
  transform: translateY(-4px);
  box-shadow: 0 5px 5px rgba(0, 0, 0, 0.2);
}

</style>
