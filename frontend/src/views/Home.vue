<template>
  <div class="home">
    <div class="welcome-container">
      <h1>Добро пожаловать!</h1>
      <p>Присоединяйтесь к LiveChat, чтобы общаться с друзьями и коллегами
        в реальном времени. Создавайте свой аккаунт или войдите, чтобы начать!</p>
      <div class="buttons">
        <router-link to="/login">
          <button class="btn-main">Войти</button>
        </router-link>
        <router-link to="/register">
          <button class="btn-secondary">Зарегистрироваться</button>
        </router-link>
      </div>
    </div>
  </div>
</template>

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

.btn-secondary {
  padding: 12px 30px;
  font-size: 16px;
  font-weight: bold;
  text-transform: uppercase;
  border: none;
  cursor: pointer;
  border-radius: 25px;
  transition: transform 0.3s ease, background-color 0.3s ease, box-shadow 0.3s ease;
}

.btn-secondary {
  background-color: white;
  color: #37a5de;
  border: white;
}

.btn-secondary:hover {
  background-color: #3fb1f1;
  color: white;
  transform: translateY(-4px);
  box-shadow: 0 5px 5px rgba(0, 0, 0, 0.2);
}
</style>
