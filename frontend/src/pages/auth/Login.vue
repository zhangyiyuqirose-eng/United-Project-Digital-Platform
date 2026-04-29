<template>
  <div class="login-page">
    <!-- 动态背景 -->
    <div class="bg-decoration">
      <div class="bg-gradient"></div>
      <div class="bg-pattern"></div>
      <div class="animated-blobs">
        <div class="blob blob-1"></div>
        <div class="blob blob-2"></div>
        <div class="blob blob-3"></div>
        <div class="blob blob-4"></div>
      </div>
    </div>

    <!-- 登录卡片 -->
    <div class="login-container">
      <div class="login-card">
        <!-- 加载进度条 -->
        <div v-show="loading" class="loading-bar">
          <div class="loading-bar-inner"></div>
        </div>

        <!-- Logo区域 -->
        <div class="logo-section">
          <div class="logo-icon">
            <svg viewBox="0 0 48 48" fill="none">
              <rect width="48" height="48" rx="12" fill="url(#logoGradient)"/>
              <path d="M12 16h24v4H12v-4zm0 8h18v4H12v-4zm0 8h12v4H12v-4z" fill="white" opacity="0.9"/>
              <defs>
                <linearGradient id="logoGradient" x1="0" y2="48">
                  <stop offset="0%" stop-color="#1a365d"/>
                  <stop offset="100%" stop-color="#3182ce"/>
                </linearGradient>
              </defs>
            </svg>
          </div>
          <h1 class="logo-title">UPDG</h1>
          <p class="logo-subtitle">一站式项目数字化运营管理平台</p>
        </div>

        <!-- 登录表单 -->
        <div class="form-section">
          <el-form
            ref="formRef"
            :model="form"
            :rules="rules"
            class="login-form"
            @keyup.enter="handleLogin"
          >
            <el-form-item prop="username">
              <el-input
                v-model="form.username"
                placeholder="请输入用户名"
                size="large"
                class="custom-input"
              >
                <template #prefix>
                  <div class="input-icon">
                    <svg viewBox="0 0 24 24" fill="currentColor">
                      <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>
                    </svg>
                  </div>
                </template>
              </el-input>
            </el-form-item>

            <el-form-item prop="password">
              <el-input
                v-model="form.password"
                type="password"
                placeholder="请输入密码"
                size="large"
                show-password
                class="custom-input"
              >
                <template #prefix>
                  <div class="input-icon">
                    <svg viewBox="0 0 24 24" fill="currentColor">
                      <path d="M18 8h-1V6c0-2.76-2.24-5-5-5S7 3.24 7 6v2H6c-1.1 0-2 .9-2 2v10c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V10c0-1.1-.9-2-2-2zm-6 9c-1.1 0-2-.9-2-2s.9-2 2-2 2 .9 2 2-.9 2-2 2zm3.1-9H8.9V6c0-1.71 1.39-3.1 3.1-3.1 1.71 0 3.1 1.39 3.1 3.1v2z"/>
                    </svg>
                  </div>
                </template>
              </el-input>
            </el-form-item>

            <div class="remember-row">
              <el-checkbox v-model="rememberMe">记住登录状态</el-checkbox>
              <a href="#" class="forgot-link">忘记密码?</a>
            </div>

            <el-button
              type="primary"
              size="large"
              class="login-btn"
              :loading="loading"
              @click="handleLogin"
            >
              <span v-if="!loading">登录系统</span>
              <span v-else>正在登录...</span>
            </el-button>
          </el-form>

          <!-- 键盘提示 -->
          <p class="keyboard-hint">按 <kbd>Enter</kbd> 快速登录</p>

          <!-- 其他登录方式 -->
          <div class="other-login">
            <p class="divider-text"><span>其他登录方式</span></p>
            <div class="login-methods">
              <button class="method-btn" title="SSO登录">
                <svg viewBox="0 0 24 24" fill="currentColor">
                  <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.1c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z"/>
                </svg>
              </button>
              <button class="method-btn" title="扫码登录">
                <svg viewBox="0 0 24 24" fill="currentColor">
                  <path d="M3 11h8V3H3v8zm2-6h4v4H5V5zm8-2v8h8V3h-8zm6 6h-4V5h4v4zM3 21h8v-8H3v8zm2-6h4v4H5v-4zm13-2h-2v2h2v-2zm0 4h-2v2h2v-2zm-4 0h2v2h-2v-2zm4 4h-2v2h2v-2zm-4 0h2v2h-2v-2zm-2-4h2v2h-2v-2z"/>
                </svg>
              </button>
            </div>
          </div>
        </div>

        <!-- 底部版权 -->
        <div class="footer-section">
          <p class="copyright">© 2026 UPDG 数字化运营管理平台 | 等保三级认证系统</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import type { FormInstance, FormRules } from 'element-plus'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()
const formRef = ref<FormInstance>()
const loading = ref(false)
const rememberMe = ref(false)

const form = reactive({
  username: '',
  password: ''
})

const rules: FormRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

const handleLogin = async () => {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        await authStore.login(form.username, form.password, rememberMe.value)
        ElMessage.success('登录成功')
        router.push('/dashboard')
      } catch (err: unknown) {
        const msg = (err as { response?: { data?: { message?: string } } })?.response?.data?.message
        ElMessage.error(msg || '登录失败，请检查用户名和密码')
      } finally {
        loading.value = false
      }
    }
  })
}
</script>

<style scoped lang="scss">
@import '@/styles/design-system.scss';

.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
}

/* 背景装饰 */
.bg-decoration {
  position: absolute;
  inset: 0;
  z-index: 0;

  .bg-gradient {
    position: absolute;
    inset: 0;
    background: linear-gradient(135deg, #0d2137 0%, #1a365d 30%, #2c5282 60%, #3182ce 100%);
  }

  .bg-pattern {
    position: absolute;
    inset: 0;
    background-image:
      radial-gradient(circle at 20% 80%, rgba(255,255,255,0.05) 0%, transparent 50%),
      radial-gradient(circle at 80% 20%, rgba(255,255,255,0.08) 0%, transparent 50%);
  }

  /* 有机渐变 Blob 动画 */
  .animated-blobs {
    position: absolute;
    inset: 0;
    overflow: hidden;

    .blob {
      position: absolute;
      border-radius: 50%;
      filter: blur(80px);
      opacity: 0.35;
      mix-blend-mode: screen;
    }

    .blob-1 {
      width: 600px;
      height: 600px;
      background: radial-gradient(circle, rgba(49, 130, 206, 0.8) 0%, rgba(49, 130, 206, 0) 70%);
      top: -15%;
      right: -10%;
      animation: blobMove1 25s ease-in-out infinite;
    }

    .blob-2 {
      width: 500px;
      height: 500px;
      background: radial-gradient(circle, rgba(99, 179, 237, 0.7) 0%, rgba(99, 179, 237, 0) 70%);
      bottom: -20%;
      left: -5%;
      animation: blobMove2 30s ease-in-out infinite;
    }

    .blob-3 {
      width: 400px;
      height: 400px;
      background: radial-gradient(circle, rgba(66, 153, 225, 0.6) 0%, rgba(66, 153, 225, 0) 70%);
      top: 40%;
      left: 20%;
      animation: blobMove3 20s ease-in-out infinite;
    }

    .blob-4 {
      width: 350px;
      height: 350px;
      background: radial-gradient(circle, rgba(26, 54, 93, 0.7) 0%, rgba(26, 54, 93, 0) 70%);
      top: 10%;
      left: 50%;
      animation: blobMove4 22s ease-in-out infinite;
    }
  }
}

@keyframes blobMove1 {
  0%, 100% { transform: translate(0, 0) scale(1); }
  25% { transform: translate(-80px, 60px) scale(1.1); }
  50% { transform: translate(-40px, 100px) scale(0.95); }
  75% { transform: translate(60px, 40px) scale(1.05); }
}

@keyframes blobMove2 {
  0%, 100% { transform: translate(0, 0) scale(1); }
  25% { transform: translate(100px, -50px) scale(1.05); }
  50% { transform: translate(60px, -100px) scale(1.15); }
  75% { transform: translate(-40px, -30px) scale(0.9); }
}

@keyframes blobMove3 {
  0%, 100% { transform: translate(0, 0) scale(1); }
  33% { transform: translate(70px, -80px) scale(1.1); }
  66% { transform: translate(-50px, 50px) scale(0.9); }
}

@keyframes blobMove4 {
  0%, 100% { transform: translate(0, 0) scale(1); }
  33% { transform: translate(-60px, 70px) scale(1.15); }
  66% { transform: translate(40px, -40px) scale(0.85); }
}

/* 登录容器 */
.login-container {
  z-index: 1;
  padding: 20px;
  width: 100%;
  max-width: 480px;
}

.login-card {
  position: relative;
  background: rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(40px) saturate(150%);
  -webkit-backdrop-filter: blur(40px) saturate(150%);
  border-radius: 24px;
  border: 1px solid rgba(255, 255, 255, 0.18);
  box-shadow:
    0 25px 60px rgba(0, 0, 0, 0.3),
    0 0 0 1px rgba(255, 255, 255, 0.05),
    inset 0 1px 0 rgba(255, 255, 255, 0.1);
  padding: 48px 40px;
  animation: cardEnter 0.6s ease-out;
  overflow: hidden;

  /* 边框发光效果 */
  &::before {
    content: '';
    position: absolute;
    inset: -1px;
    border-radius: 25px;
    padding: 1px;
    background: linear-gradient(
      135deg,
      rgba(255, 255, 255, 0.25) 0%,
      rgba(255, 255, 255, 0) 50%,
      rgba(255, 255, 255, 0.1) 100%
    );
    -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
    -webkit-mask-composite: xor;
    mask-composite: exclude;
    pointer-events: none;
    animation: glowPulse 4s ease-in-out infinite;
  }
}

@keyframes glowPulse {
  0%, 100% { opacity: 0.6; }
  50% { opacity: 1; }
}

@keyframes cardEnter {
  from {
    opacity: 0;
    transform: translateY(30px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

/* 加载进度条 */
.loading-bar {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: rgba(49, 130, 206, 0.15);
  overflow: hidden;
  border-radius: 24px 24px 0 0;

  .loading-bar-inner {
    height: 100%;
    width: 30%;
    background: linear-gradient(90deg, #3182ce, #63b3ed, #3182ce);
    border-radius: 2px;
    animation: loadingSlide 1.2s ease-in-out infinite;
    box-shadow: 0 0 8px rgba(49, 130, 206, 0.6);
  }
}

@keyframes loadingSlide {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(400%); }
}

/* Logo区域 */
.logo-section {
  text-align: center;
  margin-bottom: 40px;

  .logo-icon {
    width: 64px;
    height: 64px;
    margin: 0 auto 16px;
    animation: logoPop 0.5s ease-out 0.2s both;

    svg {
      width: 100%;
      height: 100%;
      filter: drop-shadow(0 4px 12px rgba(26, 54, 93, 0.3));
    }
  }

  .logo-title {
    font-size: 28px;
    font-weight: 700;
    letter-spacing: 2px;
    margin-bottom: 8px;
    background: linear-gradient(135deg, #ffffff 0%, rgba(255, 255, 255, 0.7) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }

  .logo-subtitle {
    font-size: 14px;
    color: rgba(255, 255, 255, 0.6);
    font-weight: 500;
  }
}

@keyframes logoPop {
  from {
    opacity: 0;
    transform: scale(0.5);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

/* 表单区域 */
.form-section {
  .login-form {
    .custom-input {
      .el-input__wrapper {
        background: rgba(255, 255, 255, 0.06);
        border: 1.5px solid rgba(255, 255, 255, 0.12);
        border-radius: 12px;
        box-shadow: none;
        padding: 4px 16px;
        height: 48px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);

        &:hover {
          background: rgba(255, 255, 255, 0.1);
          border-color: rgba(255, 255, 255, 0.2);
        }

        &.is-focus {
          background: rgba(255, 255, 255, 0.12);
          border-color: rgba(99, 179, 237, 0.6);
          box-shadow:
            0 0 0 3px rgba(99, 179, 237, 0.15),
            0 0 20px rgba(99, 179, 237, 0.1);
        }

        .el-input__inner {
          font-size: 15px;
          color: #ffffff;
          &::placeholder {
            color: rgba(255, 255, 255, 0.35);
          }
        }
      }

      /* 覆盖 Element Plus 默认的 prefix 颜色 */
      :deep(.el-input__prefix-inner) {
        color: rgba(255, 255, 255, 0.4);
      }
    }

    .input-icon {
      width: 20px;
      height: 20px;
      color: rgba(255, 255, 255, 0.4);
      display: flex;
      align-items: center;
      justify-content: center;
      transition: color 0.3s ease;

      svg {
        width: 18px;
        height: 18px;
      }
    }
  }

  .remember-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin: 16px 0 24px;

    :deep(.el-checkbox__label) {
      color: rgba(255, 255, 255, 0.6);
    }

    :deep(.el-checkbox__inner) {
      background-color: rgba(255, 255, 255, 0.08);
      border-color: rgba(255, 255, 255, 0.2);
    }

    :deep(.el-checkbox__input.is-checked .el-checkbox__inner) {
      background-color: #3182ce;
      border-color: #3182ce;
    }

    .forgot-link {
      color: rgba(99, 179, 237, 0.8);
      font-size: 14px;
      text-decoration: none;
      transition: color 0.2s;

      &:hover {
        color: #63b3ed;
      }
    }
  }

  .login-btn {
    width: 100%;
    height: 52px;
    font-size: 16px;
    font-weight: 600;
    border-radius: 12px;
    background: linear-gradient(135deg, #1a365d 0%, #2c5282 50%, #3182ce 100%);
    border: none;
    color: white;
    letter-spacing: 1px;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    position: relative;
    overflow: hidden;

    /* 双层 shimmer 效果 */
    &::before {
      content: '';
      position: absolute;
      top: 0;
      left: -100%;
      width: 60%;
      height: 100%;
      background: linear-gradient(
        90deg,
        transparent 0%,
        rgba(255, 255, 255, 0) 30%,
        rgba(255, 255, 255, 0.25) 50%,
        rgba(255, 255, 255, 0) 70%,
        transparent 100%
      );
      transition: left 0.6s ease;
    }

    &::after {
      content: '';
      position: absolute;
      inset: 0;
      border-radius: 12px;
      opacity: 0;
      background: linear-gradient(135deg, rgba(255, 255, 255, 0.15) 0%, transparent 60%);
      transition: opacity 0.3s ease;
    }

    &:hover {
      transform: translateY(-2px);
      box-shadow:
        0 8px 30px rgba(26, 54, 93, 0.5),
        0 0 20px rgba(49, 130, 206, 0.3);

      &::before {
        left: 120%;
      }

      &::after {
        opacity: 1;
      }
    }

    &:active {
      transform: translateY(0);
      box-shadow: 0 4px 15px rgba(26, 54, 93, 0.4);
    }
  }
}

/* 键盘提示 */
.keyboard-hint {
  text-align: center;
  margin-top: 16px;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.35);
  transition: color 0.2s;

  kbd {
    display: inline-block;
    padding: 2px 8px;
    margin: 0 4px;
    font-family: inherit;
    font-size: 11px;
    font-weight: 600;
    color: rgba(255, 255, 255, 0.5);
    background: rgba(255, 255, 255, 0.08);
    border: 1px solid rgba(255, 255, 255, 0.15);
    border-radius: 4px;
    box-shadow: 0 1px 0 rgba(255, 255, 255, 0.1);
  }
}

/* 其他登录方式 */
.other-login {
  margin-top: 24px;

  .divider-text {
    text-align: center;
    position: relative;
    margin-bottom: 20px;

    &::before,
    &::after {
      content: '';
      position: absolute;
      top: 50%;
      width: calc(50% - 60px);
      height: 1px;
      background: rgba(255, 255, 255, 0.12);
    }

    &::before { left: 0; }
    &::after { right: 0; }

    span {
      background: transparent;
      padding: 0 16px;
      color: rgba(255, 255, 255, 0.4);
      font-size: 13px;
    }
  }

  .login-methods {
    display: flex;
    justify-content: center;
    gap: 16px;

    .method-btn {
      width: 48px;
      height: 48px;
      border-radius: 12px;
      background: rgba(255, 255, 255, 0.06);
      border: 1px solid rgba(255, 255, 255, 0.12);
      cursor: pointer;
      transition: all 0.25s ease;
      display: flex;
      align-items: center;
      justify-content: center;
      color: rgba(255, 255, 255, 0.45);

      svg {
        width: 24px;
        height: 24px;
      }

      &:hover {
        background: rgba(255, 255, 255, 0.12);
        border-color: rgba(99, 179, 237, 0.4);
        color: #63b3ed;
        transform: translateY(-2px);
        box-shadow: 0 4px 16px rgba(99, 179, 237, 0.2);
      }
    }
  }
}

/* 底部版权 */
.footer-section {
  text-align: center;
  margin-top: 24px;

  .copyright {
    font-size: 12px;
    color: rgba(255, 255, 255, 0.3);
  }
}

/* 响应式 */
@media (max-width: 480px) {
  .login-card {
    padding: 32px 24px;
    border-radius: 16px;
  }

  .logo-section .logo-title {
    font-size: 24px;
  }
}
</style>
