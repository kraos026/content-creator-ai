<template>
  <div id="app">
    <nav class="navbar">
      <h1>Content Creator AI</h1>
    </nav>
    <YouTubeAnalytics />
  </div>
</template>

<script>
import YouTubeAnalytics from './components/YouTubeAnalytics.vue'

export default {
  name: 'App',
  components: {
    YouTubeAnalytics
  }
}
</script>

<style>
#app {
  font-family: Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
  background-color: #f5f5f5;
  min-height: 100vh;
}

.navbar {
  background-color: #ff0000;
  color: white;
  padding: 1rem;
  margin-bottom: 2rem;
}

.navbar h1 {
  margin: 0;
  text-align: center;
}

body {
  margin: 0;
  padding: 0;
}
</style>
