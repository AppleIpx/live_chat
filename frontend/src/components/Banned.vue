<template>
  <div class="banned-account">
    <div class="banned-account-container">
      <div class="icon">
        <i class="fa-regular fa-circle-xmark"></i>
        <h1>403</h1>
      </div>
      <p>Ваш аккаунт был заблокирован по следующей причине:</p>
      <p class="reason">{{ reason }}</p>
      <br/>
      <router-link to="/" class="btn">Вернуться на главную</router-link>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      reason: "Неизвестная причина",
    };
  },
  created() {
    if (this.$route?.query?.reason) {
      this.reason = this.$route.query.reason;
    }
  },
};
</script>

<style scoped>
.banned-account {
  text-align: center;
  background: linear-gradient(135deg, #73b5e1, #b6d5de);
  height: 100vh;
  overflow: hidden;
}

.banned-account-container {
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
  color: #d32f2f;
  margin-top: 20%;
  font-size: 6rem;
}

h1 {
  font-size: 8rem;
  color: #c62828;
}

p {
  font-size: 1.5rem;
  margin: 20px 0;
}

.reason {
  font-size: 1.5rem;
  font-style: italic;
  color: #d32f2f;
}

.btn {
  padding: 12px 30px;
  font-size: 16px;
  font-weight: bold;
  text-transform: uppercase;
  color: #fff;
  background-color: #d32f2f;
  border: none;
  cursor: pointer;
  text-decoration: none;
  border-radius: 25px;
  transition: transform 0.3s ease, background-color 0.3s ease, box-shadow 0.3s ease;
}

.btn:hover {
  background-color: #c62828;
  transform: translateY(-4px);
  box-shadow: 0 5px 5px rgba(0, 0, 0, 0.2);
}
</style>
