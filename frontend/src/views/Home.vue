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
        // Для примера получим имя пользователя из localStorage, если оно там хранится
        this.username = localStorage.getItem('username') || 'пользователь';
      }
    },
  },
};
</script>

<style scoped>
.home {
  background-color: #f7f7f7;
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  padding: 20px;
}

.welcome-container {
  background-color: #dbe3f3;
  padding: 40px;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 600px;
  text-align: center;
}

h1 {
  color: #333;
  font-size: 32px;
  margin-bottom: 15px;
  font-weight: bold;
  text-transform: uppercase;
  letter-spacing: 1px;
}

p {
  font-size: 18px;
  color: #666;
  margin-bottom: 30px;
}

.buttons {
  display: flex;
  justify-content: center;
  gap: 20px;
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
