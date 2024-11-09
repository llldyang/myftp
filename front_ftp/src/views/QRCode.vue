<template>
    <div class="qr-container">
        <div class="qr-card">
            <div class="setup-header">
                <h2 class="setup-title">设置双重身份验证</h2>
                <p class="setup-subtitle">请使用身份验证器 App 扫描以下二维码</p>
            </div>

            <div class="qr-section">
                <div class="qr-frame" v-if="qrCodeImage">
                    <img :src="qrCodeImage" alt="QR Code" class="qr-image" />
                    <div class="scan-overlay">
                        <div class="scan-line"></div>
                    </div>
                </div>

                <div class="steps-guide">
                    <div class="step">
                        <span class="step-number">1</span>
                        <span class="step-text">打开身份验证器 App</span>
                    </div>
                    <div class="step">
                        <span class="step-number">2</span>
                        <span class="step-text">扫描二维码</span>
                    </div>
                    <div class="step">
                        <span class="step-number">3</span>
                        <span class="step-text">输入验证码完成设置</span>
                    </div>
                </div>
            </div>

            <button @click="goTo2FAPage" class="continue-btn">
                已完成扫描，继续验证
                <span class="arrow">→</span>
            </button>
        </div>
    </div>
</template>

<script>
import axios from 'axios';

export default {
    data() {
        return {
            qrCodeImage: null,  // 保存二维码图片数据
            username: '',  // 从路由参数中获取用户名
            totp: '',  // 保存用户输入的 TOTP 代码
            accessToken: '' // 用于存储 JWT token
        };
    },
    mounted() {
        // 获取二维码图像
        axios
            .get('https://localhost:5000/auth/show_qr_code', {
                responseType: 'blob',
                withCredentials: true  // 保留跨域请求的会话信息
            })
            .then((response) => {
                // 将二维码图像转换为 URL 对象
                this.qrCodeImage = URL.createObjectURL(response.data);
            })
            .catch((error) => {
                console.error("Failed to load QR Code", error);
            });

        // 获取会话数据（用户名和 TOTP 秘钥）新用户
        axios
            .get('https://localhost:5000/auth/get_session_data', { withCredentials: true })
            .then(response => {
                this.username = response.data.username;  // 获取用户名
                this.totpSecret = response.data.totp_secret;  // 获取 TOTP 秘钥
                this.accessToken = response.data.access_token
                console.log(this.accessToken)
            })
            .catch(error => {
                console.error("Failed to load session data", error);
            });
    },

    methods: {
        // fetchQRCode() {
        //     console.log("发送请求至后端获取二维码...");
        //     axios.get('https://localhost:5000/auth/login/authorized', {
        //         withCredentials: true
        //     })
        //         .then((response) => {
        //             console.log("响应内容:", response.data);
        //             if (response.data && response.data.qr_code) {
        //                 this.qrCodeImage = response.data.qr_code;
        //                 this.username = response.data.username || '';
        //                 this.accessToken = response.data.token;
        //             } else {
        //                 console.error("Invalid response data", response.data);
        //             }
        //         })
        //         .catch((error) => {
        //             console.error("Failed to load QR Code", error);
        //         });
        // },
        goTo2FAPage() {
            // 检查用户名和 TOTP 是否填写
            // if (!this.username || !this.totp) {
            //     alert('请填写用户名和 TOTP 代码');
            //     return;
            // }

            // 发送 POST 请求以验证 TOTP
            // console.log("goTo2FAPage中是否存在username")
            console.log(this.username)
            // console.log(this.totpSecret)
            // console.log(this.accessToken)
            // axios.post('https://localhost:5000/auth/2fa/verify', {
            //     username: this.username,
            //     totp: this.totpSecret
            // }, {
            //     headers: {
            //         'Authorization': `Bearer ${this.accessToken}` // 将 JWT Token 添加到请求头
            //     }
            // })
            //     .then(response => {
            //         console.log(response.data);  // 打印后端返回的消息
            //         // 跳转到 2FA 验证成功后的页面
            //         this.$router.push({ path: '/auth/file-manager' });  // 你可以修改为实际需要跳转的路径
            //     })
            //     .catch(error => {
            //         if (error.response) {
            //             console.error("请求错误:", error.response.data);  // 打印后端返回的错误信息
            //         } else if (error.request) {
            //             console.error("请求未得到响应:", error.request);  // 请求未得到响应
            //         } else {
            //             console.error("错误信息:", error.message);  // 打印错误信息
            //         }
            //     });
            // 跳转到 2FA 页面,因为用户扫描二维码后点击button应跳转到验证页面
            localStorage.setItem('username', this.username);
            localStorage.setItem('token', this.accessToken);
            this.$router.push({ path: '/auth/2fa' });

        },
    },
};
</script>

<style scoped>
.qr-container {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 100vh;
    background-color: #f5f7fa;
    padding: 1rem;
}

.qr-card {
    background-color: white;
    padding: 2.5rem;
    border-radius: 8px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    width: 100%;
    max-width: 480px;
}

.setup-header {
    text-align: center;
    margin-bottom: 2rem;
}

.setup-title {
    color: #2c3e50;
    font-size: 1.5rem;
    margin-bottom: 0.75rem;
    font-weight: 600;
}

.setup-subtitle {
    color: #606f7b;
    font-size: 1rem;
}

.qr-section {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 2rem;
    margin-bottom: 2rem;
}

.qr-frame {
    position: relative;
    padding: 1rem;
    background: white;
    border: 2px solid #e2e8f0;
    border-radius: 8px;
    width: fit-content;
}

.qr-image {
    display: block;
    width: 200px;
    height: 200px;
    object-fit: contain;
}

.scan-overlay {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    pointer-events: none;
}

.scan-line {
    position: absolute;
    left: 0;
    right: 0;
    height: 2px;
    background: #4299e1;
    animation: scan 2s linear infinite;
}

@keyframes scan {
    0% {
        top: 0;
        opacity: 1;
    }

    50% {
        opacity: 0.5;
    }

    100% {
        top: 100%;
        opacity: 1;
    }
}

.steps-guide {
    display: flex;
    flex-direction: column;
    gap: 1rem;
    width: 100%;
}

.step {
    display: flex;
    align-items: center;
    gap: 1rem;
}

.step-number {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 24px;
    height: 24px;
    background-color: #4299e1;
    color: white;
    border-radius: 50%;
    font-size: 0.875rem;
    font-weight: 600;
}

.step-text {
    color: #4a5568;
    font-size: 0.95rem;
}

.continue-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 100%;
    padding: 0.875rem 1.5rem;
    background-color: #4299e1;
    color: white;
    border: none;
    border-radius: 4px;
    font-size: 1rem;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.3s ease;
}

.continue-btn:hover {
    background-color: #3182ce;
}

.continue-btn:active {
    background-color: #2c5282;
}

.arrow {
    margin-left: 0.5rem;
    transition: transform 0.3s ease;
}

.continue-btn:hover .arrow {
    transform: translateX(4px);
}

@media (max-width: 480px) {
    .qr-card {
        padding: 1.5rem;
    }

    .qr-image {
        width: 180px;
        height: 180px;
    }

    .setup-title {
        font-size: 1.25rem;
    }

    .setup-subtitle {
        font-size: 0.9rem;
    }
}
</style>