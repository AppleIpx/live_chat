<template>
  <div class="register">
    <div class="register-container">
      <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>
      <h2>Регистрация</h2>
      <form @submit.prevent="registerUser" class="form">
        <input v-model="username" placeholder="Имя пользователя" class="input-field" />
        <input v-model="email" type="email" placeholder="Email" class="input-field" />
        <input v-model="first_name" placeholder="Имя" class="input-field" />
        <input v-model="last_name" placeholder="Фамилия" class="input-field" />
        <input v-model="password" type="password" placeholder="Пароль" class="input-field" />
        <input v-model="confirmPassword" type="password" placeholder="Повторите пароль" class="input-field" />
        <button type="submit" class="btn-main">Зарегистрироваться</button>
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
      confirmPassword: '',
      email: '',
      first_name: '',
      last_name: '',
      errorMessage: '',
    };
  },
  methods: {
    validateForm() {
      if (!this.username || !this.email || !this.first_name || !this.last_name || !this.password || !this.confirmPassword) {
        this.errorMessage = 'Все поля должны быть заполнены';
        return false;
      }

      const emailRegex = /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,6}$/;
      if (!emailRegex.test(this.email)) {
        this.errorMessage = 'Пожалуйста, введите правильный email';
        return false;
      }

      if (this.password !== this.confirmPassword) {
        this.errorMessage = 'Пароли не совпадают';
        return false;
      }

      this.errorMessage = '';
      return true;
    },

    async registerUser() {
      if (!this.validateForm()) {
        return;
      }

      try {
        const response = await axios.post('http://0.0.0.0:8000/api/auth/register', {
          username: this.username,
          password: this.password,
          email: this.email,
          first_name: this.first_name,
          last_name: this.last_name,
        });

        if (response.status === 201) {
          this.$router.push("/login");
        }
      } catch (error) {
        if (error.response) {
          if (error.response.status === 400) {
            if (error.response.data.detail) {
              const errorDetail = error.response.data.detail;
              if (errorDetail.code === 'REGISTER_INVALID_PASSWORD') {
                this.errorMessage = 'Пароль должен содержать минимум 3 символа';
              } else if (errorDetail === 'REGISTER_USER_ALREADY_EXISTS') {
                this.errorMessage = 'Пользователь с таким email уже существует';
              } else {
                this.errorMessage = 'Ошибка регистрации, попробуйте снова';
              }
            } else {
              this.errorMessage = 'Ошибка при регистрации';
            }
          } else if (error.response.status === 422) {
            this.errorMessage = 'Неверные данные, проверьте введенные значения';
          } else {
            this.errorMessage = 'Произошла ошибка при регистрации, попробуйте снова';
          }
        } else {
          this.errorMessage = 'Ошибка при подключении к серверу';
        }
      }
    },
  },
};
</script>

<style scoped>
.register {
  background-color: #f7f7f7;
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  padding: 20px;
}

.register-container {
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

.register h2 {
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
  .register-container {
    padding: 30px;
    width: 100%;
  }

  .register h2 {
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
