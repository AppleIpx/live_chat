<template>
  <div class="deleted-account">
    <div class="deleted-account-container">
      <div class="icon">
        <i class="fa fa-times-circle"></i>
        <h1>Аккаунт удален</h1>
      </div>
      <p>Этот аккаунт больше недоступен.</p>
      <br>
      <router-link to="/" class="btn">Вернуться на главную</router-link>
    </div>
  </div>
</template>

<script>
export default {};
</script>

<style scoped>
.deleted-account {
  text-align: center;
  background: linear-gradient(135deg, #73b5e1, #b6d5de);
  height: 100vh;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
}

.deleted-account-container {
  background-color: #f5f5f5;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  width: 90%;
  max-width: 600px;
  height: auto;
  padding: 30px;
  border-radius: 15px;
  text-align: center;
}

.icon {
  font-size: 5rem;
  color: #9e9e9e;
  margin-bottom: 20px;
}

h1 {
  font-size: 2.5rem;
  color: #616161;
  margin-bottom: 10px;
}

p {
  font-size: 1.2rem;
  color: #757575;
  margin: 10px 0;
}

.btn {
  padding: 12px 30px;
  font-size: 16px;
  font-weight: bold;
  text-transform: uppercase;
  color: #fff;
  background-color: #757575;
  border: none;
  cursor: pointer;
  text-decoration: none;
  border-radius: 25px;
  transition: transform 0.3s ease, background-color 0.3s ease, box-shadow 0.3s ease;
}

.btn:hover {
  background-color: #616161;
  transform: translateY(-4px);
  box-shadow: 0 5px 5px rgba(0, 0, 0, 0.2);
}
</style>
