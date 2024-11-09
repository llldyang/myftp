<template>
  <div class="login-container">
    <div class="login-card">
      <h1 class="login-title">欢迎使用文件传输系统</h1>
      <button class="github-login-btn" @click="login">
        <span class="github-icon">
          <i class="fab fa-github"></i>
        </span>
        使用GitHub登录
      </button>
    </div>
  </div>
</template>

<script>
export default {
  methods: {
    login() {
      localStorage.clear()
      // 直接将浏览器页面重定向到后端的登录路径
      window.location.href = "https://localhost:5000/auth/login";
    },

  }

};
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: #f5f7fa;
}

.login-card {
  background-color: white;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  text-align: center;
  width: 100%;
  max-width: 400px;
}

.login-title {
  color: #2c3e50;
  font-size: 1.8rem;
  margin-bottom: 2rem;
  font-weight: 600;
}

.github-login-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  padding: 0.8rem 1.5rem;
  font-size: 1rem;
  color: white;
  background-color: #24292e;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.github-login-btn:hover {
  background-color: #1a1f23;
}

.github-icon {
  margin-right: 0.5rem;
}

/* 确保添加 Font Awesome 的 CDN */
@import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css');
</style>