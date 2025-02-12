<!-- src/App.vue -->
<template>
  <head>
    <link rel="stylesheet"
          href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
    <title>Live Chat</title>
  </head>
  <div id="app">
    <Header/>
    <ChatNotification/>
    <router-view/>
  </div>
</template>

<script>
import Header from './components/Header.vue';
import ChatNotification from './components/ChatNotification.vue';
import SSEManager from "@/services/sseService";


export default {
  components: {
    Header,
    ChatNotification,
  },
  beforeUnmount() {
    SSEManager.disconnectAll();
  },
};
</script>

<style>
body {
  font-family: 'Roboto', sans-serif;
  margin: 0;
  padding: 0;
  background-color: #f7f7f7;
  color: #333;
}

button {
  background-color: #0088cc;
  color: white;
  padding: 10px 20px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

#app {
  padding-top: 10px;
}

button:hover {
  background-color: #007bb5;
}

a {
  color: #0088cc;
  text-decoration: none;
}

a:hover {
  text-decoration: underline;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}
</style>
