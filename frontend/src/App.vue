<template>
  <div class="app-container">
    <header class="app-header">
      <div class="logo">
        <h1>Jailbreak System</h1>
      </div>
      <nav class="main-nav">
        <router-link to="/">Home</router-link>
        <router-link to="/attacks">Attacks</router-link>
        <router-link to="/prompts">Prompts</router-link>
        <router-link to="/results">Results</router-link>
        <router-link to="/stats">Statistics</router-link>
      </nav>
    </header>
    
    <main class="app-content">
      <Toast />
      <router-view />
    </main>
    
    <footer class="app-footer">
      <p>&copy; {{ new Date().getFullYear() }} Sandy Zheng, Grad Design for HFUT.</p>
    </footer>
  </div>
</template>

<script>
export default {
  name: 'App'
}
</script>

<style>
html, body {
  margin: 0;
  padding: 0;
  height: 100%;
  font-family: 'Avenir', Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
}

.app-container {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.app-header {
  background-color: #1e293b;
  color: white;
  padding: 1rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logo h1 {
  margin: 0;
  font-size: 1.5rem;
}

.main-nav {
  display: flex;
  gap: 1.5rem;
}

.main-nav a {
  color: white;
  text-decoration: none;
  font-weight: 500;
  padding: 0.5rem 0;
  border-bottom: 2px solid transparent;
  transition: border-color 0.3s;
}

.main-nav a:hover,
.main-nav a.router-link-active {
  border-color: #4f46e5;
}

.app-content {
  flex: 1;
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
}

.app-footer {
  background-color: #f8f9fa;
  padding: 1rem;
  text-align: center;
  font-size: 0.9rem;
  color: #6c757d;
}
</style> 