<template>
  <div class="not-found">
    <div class="not-found-container">
      <div class="icon">
        <i class="fa fa-exclamation-triangle"></i>
      </div>
      <h1>404</h1>
      <p>Страница не найдена.</p>
      <router-link to="/" class="btn">Вернуться на главную</router-link>
    </div>
  </div>
</template>

<script>
export default {
  name: "NotFound",
};
</script>

<style scoped>
.not-found {
  text-align: center;
  background: linear-gradient(135deg, #73b5e1, #b6d5de);
  height: 100vh;
  overflow: hidden;
}

.not-found-container {
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
  color: #fbc02d;
}

h1 {
  font-size: 8rem;
  color: #fbc02d;
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
  background-color: #fbc02d;
  border: none;
  cursor: pointer;
  text-decoration: none;
  border-radius: 25px;
  transition: transform 0.3s ease, background-color 0.3s ease, box-shadow 0.3s ease;
}

.btn:hover {
  background-color: #f57f17;
  transform: translateY(-4px);
  box-shadow: 0 5px 5px rgba(0, 0, 0, 0.2);
}
</style>
