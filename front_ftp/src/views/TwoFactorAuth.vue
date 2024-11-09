<template>
  <div class="two-factor-container">
    <div class="two-factor-card">
      <div class="welcome-section">
        <h2 class="welcome-text">欢迎, {{ username }}!</h2>
        <h3 class="instruction-text">请输入 TOTP 代码进行验证</h3>
      </div>

      <form @submit.prevent="verifyTotp" class="totp-form">
        <div class="input-group">
          <label for="totp" class="input-label">TOTP 代码：</label>
          <input v-model="totp" type="text" id="totp" class="totp-input" maxlength="6" pattern="\d{6}"
            placeholder="请输入6位数字验证码" required />
        </div>
        <button type="submit" class="verify-btn">验证</button>
      </form>

      <transition name="fade">
        <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>
      </transition>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      totp: '',
      username: '',
      errorMessage: '',
      token: '',
    };
  },

  created() {
    if (this.accessToken) {
      console.log("get Token from url444444:", this.token);//老用户
    }
    // 获取 URL 参数中的 token 并存储在 localStorage 中
    // const urlParams = new URLSearchParams(window.location.search);
    // this.token = urlParams.get('token');
    // const urlToken = urlParams.get('token');
    // console.log("get Token from url:", this.token);//老用户
    // if (urlToken) {
    //   // 如果 URL 中有 token，存储并使用它
    //   this.token = urlToken;
    //   localStorage.setItem('token', urlToken);
    //   console.log("Token from URL stored:", urlToken);
    //   // 立即使用新 token 获取用户信息
    //   this.getUsername();
    // } else {
    //   // 如果 URL 中没有 token，尝试从 localStorage 获取
    //   const storedToken = localStorage.getItem('token');
    //   if (storedToken) {
    //     this.token = storedToken;
    //     const storedUsername = localStorage.getItem('username');
    //     if (storedUsername) {
    //       this.username = storedUsername;
    //     } else {
    //       // 有 token 但没有用户名，获取用户信息
    //       this.getUsername();
    //     }
    //   } else {
    //     console.error("No token found");
    //     this.errorMessage = '未找到 token，请重新登录';
    //   }
    // }
//如果 URL 中没有 token，尝试从 localStorage 获取
      const storedToken = localStorage.getItem('token');
      if (storedToken) {
        this.token = storedToken;
        const storedUsername = localStorage.getItem('username');
        if (storedUsername) {
          this.username = storedUsername;
        } else {
          // 有 token 但没有用户名，获取用户信息
          this.getUsername();
        }
      } else {
        this.getolduserToken();
        
      }

  },
  methods: {
    getUsername() {
      axios
        .get('https://localhost:5000/auth/2fa', {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`,
          },
        })
        .then((response) => {
          this.username = response.data.username;
        })
        .catch((error) => {
          console.error("获取用户名失败", error);
          this.errorMessage = '无法加载用户信息，请重新登录';
        });
    },
    getolduserToken() {
      axios
        .get('https://localhost:5000/auth/get_session_data', { withCredentials: true })
        .then(response => {
          this.username = response.data.username;  // 获取用户名
         
          this.token = response.data.access_token
          console.log("4546546545665465")
          console.log(this.token)
        })
        .catch(error => {
          console.error("Failed to load session data", error);
        });
    },
    verifyTotp() {
      console.log('Sending TOTP Verification Request:', { totp: this.totp });
      console.log('Sending TOTP Verification Request:', { token: this.token });
      axios
        .post('https://localhost:5000/auth/2fa/verify', { totp: this.totp }, {
          headers: {
            Authorization: `Bearer ${this.token}`,
          },
        })
        .then((response) => {
          if (response.data.message === '验证成功') {
            localStorage.setItem('token', this.token);  // 将 token 保存到 localStorage
            this.$router.push({ path: '/auth/file-manager' });
          }
        })
        .catch((error) => {
          this.errorMessage = '验证失败，请检查您的 TOTP 代码';
          console.error("TOTP Verification Failed", error);
        });
    },
  },
};
</script>


<style scoped>
.two-factor-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: #f5f7fa;
  padding: 1rem;
}

.two-factor-card {
  background-color: white;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 400px;
}

.welcome-section {
  text-align: center;
  margin-bottom: 2rem;
}

.welcome-text {
  color: #2c3e50;
  font-size: 1.5rem;
  margin-bottom: 0.5rem;
  font-weight: 600;
}

.instruction-text {
  color: #606f7b;
  font-size: 1.1rem;
  margin-top: 0.5rem;
  font-weight: 500;
}

.totp-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.input-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.input-label {
  color: #4a5568;
  font-size: 0.9rem;
  font-weight: 500;
}

.totp-input {
  width: 100%;
  padding: 0.75rem;
  font-size: 1rem;
  border: 1px solid #e2e8f0;
  border-radius: 4px;
  transition: border-color 0.3s ease;
}

.totp-input:focus {
  outline: none;
  border-color: #4299e1;
  box-shadow: 0 0 0 3px rgba(66, 153, 225, 0.1);
}

.verify-btn {
  background-color: #4299e1;
  color: white;
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.verify-btn:hover {
  background-color: #3182ce;
}

.verify-btn:active {
  background-color: #2c5282;
}

.error-message {
  margin-top: 1rem;
  padding: 0.75rem;
  background-color: #fed7d7;
  border: 1px solid #fc8181;
  border-radius: 4px;
  color: #c53030;
  font-size: 0.9rem;
  text-align: center;
}

/* 错误消息的淡入淡出动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
