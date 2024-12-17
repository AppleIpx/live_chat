<template>
  <header class="header">
    <router-link class="logo-link" to="/">
      <div class="logo">
        <i class="fas fa-comments chat-icon"></i>
        <h1>Live Chat</h1>
      </div>
    </router-link>
    <nav class="nav-links">
      <div class="nav-item dropdown">
        <span class="dropdown-toggle">Чаты</span>
        <div class="dropdown-menu">
          <router-link to="/chats" class="dropdown-item">Все чаты</router-link>
          <router-link to="/chats/deleted" class="dropdown-item">Удалённые сообщения</router-link>
        </div>
      </div>
      <div class="nav-item dropdown">
        <span class="dropdown-toggle">Пользователи</span>
        <div class="dropdown-menu">
          <router-link to="/users" class="dropdown-item">Все пользователи</router-link>
          <router-link to="/black-list" class="dropdown-item">Чёрный список</router-link>
        </div>
      </div>
      <router-link to="/profile/me" class="nav-item">Мой профиль</router-link>
      <button @click="handleAuth" class="btn-auth">
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
  background: linear-gradient(135deg, #37a5de, #6dcfe1);
  color: white;
  padding: 20px 30px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-radius: 0 0 15px 15px;
  box-shadow: 0 8px 15px rgba(0, 0, 0, 0.15);
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  backdrop-filter: blur(10px);
}

.logo {
  display: flex;
  align-items: center;
}

.header .logo h1 {
  font-size: 28px;
  margin: 0;
  font-weight: bold;
  letter-spacing: 1px;
  color: white;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.2);
}

.chat-icon {
  font-size: 32px;
  margin-right: 12px;
  color: white;
  animation: bounce 2s infinite;
}

@keyframes bounce {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-5px);
  }
}

.nav-links {
  display: flex;
  gap: 25px;
  align-items: center;
}

.nav-item {
  font-size: 18px;
  color: rgba(255, 255, 255, 0.9);
  text-decoration: none;
  font-weight: 500;
  transition: color 0.3s ease, transform 0.3s ease;
}

.nav-item:hover {
  color: #ece0e0;
  transform: scale(1.05);
  text-decoration: none;
}

.btn-auth {
  background: linear-gradient(135deg, #ffffff, #f0f8ff);
  color: #37a5de;
  border: none;
  padding: 10px 25px;
  font-size: 16px;
  cursor: pointer;
  border-radius: 30px;
  font-weight: bold;
  transition: all 0.3s ease;
  box-shadow: 0 5px 10px rgba(0, 0, 0, 0.1);
}

.btn-auth:hover {
  background: #37a5de;
  color: white;
  transform: translateY(-3px);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.3);
}

.logo-link {
  color: white;
}

.logo-link:hover {
  text-decoration: none;
}

.logo-link:hover .chat-icon {
  transform: scale(1.1);
}

.dropdown {
  position: relative;
  cursor: pointer;
}

.dropdown-toggle {
  font-size: 18px;
  color: rgba(255, 255, 255, 0.9);
  font-weight: 500;
  transition: color 0.3s ease;
}

.dropdown-toggle:hover {
  color: #ece0e0;
}

.dropdown-menu {
  display: none;
  position: absolute;
  top: 100%;
  left: 0;
  background-color: #ffffff;
  border-radius: 10px;
  box-shadow: 0 8px 15px rgba(0, 0, 0, 0.2);
  overflow: hidden;
  z-index: 1000;
  min-width: 200px;
}

.dropdown:hover .dropdown-menu {
  display: block;
}

.dropdown-item {
  display: block;
  padding: 10px 15px;
  color: #333;
  text-decoration: none;
  font-size: 16px;
  transition: background-color 0.3s ease, color 0.3s ease;
}

.dropdown-item:hover {
  background-color: #37a5de;
  color: white;
}

</style>
