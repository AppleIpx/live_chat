<template>
  <div class="login">
    <div class="login-container">
      <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>
      <h2>Вход</h2>
      <form @submit.prevent="loginUser" class="form">
        <input v-model="username" placeholder="Имя пользователя" class="input-field"/>
        <input v-model="password" type="password" placeholder="Пароль"
               class="input-field"/>
        <div class="buttons">
          <button type="submit" class="btn-main">Войти</button>
        </div>
      </form>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      username: '',
      password: '',
      errorMessage: '',  // Для вывода ошибок
    };
  },
  methods: {
    async loginUser() {
      try {
        const formData = new FormData();
        formData.append('username', this.username);
        formData.append('password', this.password);

        const response = await axios.post('http://0.0.0.0:8000/api/auth/jwt/login', formData);
        if (response.status === 201) {
          const accessToken = response.data.access_token;
          localStorage.setItem('accessToken', accessToken);
          this.$router.push('/profile');
        }
      } catch (error) {
        if (error.response) {
          if (error.response.status === 400) {
            this.errorMessage = this.getErrorMessage(error.response.data.detail);
          } else if (error.response.status === 422) {
            this.errorMessage = 'Некорректные данные, пожалуйста, проверьте введенные значения';
          } else {
            this.errorMessage = 'Произошла ошибка при входе, попробуйте снова';
          }
        } else {
          this.errorMessage = 'Ошибка при подключении к серверу';
        }
      }
    },
    getErrorMessage(errorCode) {
      if (errorCode === 'LOGIN_BAD_CREDENTIALS') {
        return 'Неверный логин или пароль';
      } else if (errorCode === 'LOGIN_USER_NOT_VERIFIED') {
        return 'Пользователь не подтвержден';
      }
      return 'Ошибка при входе';
    }
  },
};
</script>

<style scoped>
.login {
  background-color: #f7f7f7;
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  padding: 20px;
}

.login-container {
  background-color: white;
  padding: 40px;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 400px;
  text-align: center;
}

.error-message {
  color: #e85342;
  font-size: 14px;
  margin-bottom: 20px;
  padding: 10px;
  background-color: #fadbde;
  border: 1px solid #ee5442;
  border-radius: 5px;
  text-align: center;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
  animation: fadeIn 0.5s ease-in-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.login h2 {
  color: #0078d4;
  font-size: 24px;
  margin-bottom: 20px;
}

.form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.input-field {
  padding: 12px;
  border-radius: 8px;
  border: 1px solid #ddd;
  font-size: 16px;
  outline: none;
  transition: border-color 0.3s ease;
}

.input-field:focus {
  border-color: #0078d4;
}

.btn-main {
  padding: 14px 30px;
  font-size: 16px;
  font-weight: bold;
  text-transform: uppercase;
  border: none;
  cursor: pointer;
  border-radius: 25px;
  background-color: #0088cc;
  color: white;
  transition: all 0.3s ease;
}

.btn-main:hover {
  background-color: #007bb5;
  transform: translateY(-4px);
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
}

@media (max-width: 600px) {
  .login-container {
    padding: 30px;
    width: 100%;
  }

  .login h2 {
    font-size: 20px;
  }

  .input-field {
    font-size: 14px;
  }

  .btn-main {
    font-size: 14px;
  }
}
</style>
