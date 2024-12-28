<template>
  <div class="forbidden">
    <div class="forbidden-container">
      <div class="icon">
        <i class="fa fa-ban"></i>
        <h1>403</h1>
      </div>
      <p>Ваш аккаунт был удалён.</p>
      <p>Чтобы восстановить доступ, выполните восстановление аккаунта.</p>
      <button class="btn" @click="recoverAccount">Восстановить аккаунт</button>
    </div>
  </div>
</template>

<script>
import {userService} from "@/services/apiService";
import router from "@/router";
import {handleError} from "@/utils/errorHandler";

export default {
  methods: {
    async recoverAccount() {
      try {
        await userService.recoverUserMe();
        alert("Аккаунт успешно восстановлен.");
        await router.push("/profile/me");
      } catch (error) {
        await handleError(error);
      }
    },
  },
};
</script>

<style scoped>
.forbidden {
  text-align: center;
  background: linear-gradient(135deg, #73b5e1, #b6d5de);
  height: 100vh;
  overflow: hidden;
}

.forbidden-container {
  background-color: white;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  margin-left: 30%;
  margin-top: 8%;
  width: 90%;
  max-width: 700px;
  height: 70%;
  max-height: 800px;
  padding: 30px;
  border-radius: 15px;
}

.icon {
  margin-top: 20%;
  font-size: 6rem;
  color: #d35d5d;
}

h1 {
  font-size: 8rem;
  color: #d35d5d;
}

p {
  font-size: 1.5rem;
  margin: 20px 0;
}

.btn {
  padding: 12px 30px;
  font-size: 16px;
  font-weight: bold;
  text-transform: uppercase;
  color: #fff;
  background-color: #e76f51;
  border: none;
  cursor: pointer;
  text-decoration: none;
  border-radius: 25px;
  transition: transform 0.3s ease, background-color 0.3s ease, box-shadow 0.3s ease;
}

.btn:hover {
  background-color: #dd614a;
  transform: translateY(-4px);
  box-shadow: 0 5px 5px rgba(0, 0, 0, 0.2);
}
</style>
