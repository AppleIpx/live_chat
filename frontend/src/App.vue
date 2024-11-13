<!-- src/App.vue -->
<template>
  <div id="app">
    <router-view/>
  </div>
</template>

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

.btn-main {
  background-color: #37a5de;
  border: #37a5de;
  color: white;
  padding: 12px 30px;
  font-size: 16px;
  font-weight: bold;
  text-transform: uppercase;
  border: none;
  cursor: pointer;
  border-radius: 25px;
  transition: transform 0.3s ease, background-color 0.3s ease, box-shadow 0.3s ease;
}

.btn-main:hover {
  background-color: white;
  color: #37a5de;
  transform: translateY(-4px);
  box-shadow: 0 5px 5px rgba(0, 0, 0, 0.2);
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
</style>
