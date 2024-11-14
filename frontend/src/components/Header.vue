<!-- src/components/Header.vue -->
<template>
  <header class="header">
    <router-link class="logo-link" to="/">
      <div class="logo">
        <i class="fas fa-comments chat-icon"></i>
        <h1>Live Chat</h1>
      </div>
    </router-link>
    <nav class="nav-links">
      <router-link to="/chats" class="nav-item">Чаты</router-link>
      <router-link to="/users" class="nav-item">Пользователи</router-link>
      <router-link to="/profile/me" class="nav-item">Мой профиль</router-link>
      <button @click="handleAuth" class="btn-main">
        {{ isAuthenticated ? 'Выйти' : 'Войти' }}
      </button>
    </nav>
  </header>
</template>

<script>
export default {
  data() {
    return {
      isAuthenticated: !!localStorage.getItem('accessToken'),
    };
  },
  methods: {
    handleAuth() {
      if (this.isAuthenticated) {
        localStorage.removeItem('accessToken');
        this.$router.push('/login');
      } else {
        this.$router.push('/login');
      }
    }
  },
  watch: {
    '$route'() {
      this.isAuthenticated = !!localStorage.getItem('accessToken');
    }
  }
};
</script>

<style scoped>
.header {
  background-color: #37a5de;
  color: white;
  padding: 15px 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-radius: 0 0 10px 10px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.logo {
  display: flex;
  align-items: center;
}

.header .logo h1 {
  font-size: 24px;
  margin: 0;
  font-weight: bold;
  letter-spacing: 1px;
}

.chat-icon {
  font-size: 26px;
  margin-right: 10px;
  color: white;
}

.nav-links {
  display: flex;
  gap: 20px;
  align-items: center;
}

.nav-item {
  font-size: 18px;
  color: white;
  text-decoration: none;
  transition: color 0.3s ease;
}

.nav-item:hover {
  color: #fff;
  text-decoration: underline;
}

.btn-main {
  background-color: white;
  color: #37a5de;
  border: none;
  padding: 10px 20px;
  font-size: 16px;
  cursor: pointer;
  border-radius: 25px;
  transition: transform 0.3s ease, background-color 0.3s ease, box-shadow 0.3s ease;
}

.btn-main:hover {
  background-color: #37a5de;
  color: white;
  transform: translateY(-4px);
  box-shadow: 0 5px 5px rgba(0, 0, 0, 0.2);
}

.logo-link {
  color: white;
}


.logo-link:hover {
  color: white;
  text-decoration: none;
}
</style>

