<template>
  <div class="login-page">
    <div class="login-left">
      <div class="brand-area">
        <div class="brand-icon-wrap">
          <el-icon :size="42" color="#fff"><TrendCharts /></el-icon>
        </div>
        <h1>电商评论情感分析系统</h1>
        <p>基于 Python 的商品评论情感分析与用户需求挖掘平台</p>
      </div>
      <div class="feature-list">
        <div class="feature-item">
          <el-icon :size="24" color="#a3e4c1"><Search /></el-icon>
          <span>智能数据采集</span>
        </div>
        <div class="feature-item">
          <el-icon :size="24" color="#a3e4c1"><DataAnalysis /></el-icon>
          <span>NLP 情感分析</span>
        </div>
        <div class="feature-item">
          <el-icon :size="24" color="#a3e4c1"><Aim /></el-icon>
          <span>需求深度挖掘</span>
        </div>
        <div class="feature-item">
          <el-icon :size="24" color="#a3e4c1"><PieChart /></el-icon>
          <span>可视化分析报告</span>
        </div>
      </div>
    </div>

    <div class="login-right">
      <div class="login-card">
        <h2>{{ isRegister ? '注册账号' : '欢迎回来' }}</h2>
        <p class="subtitle">{{ isRegister ? '创建您的分析系统账号' : '登录您的分析系统账号' }}</p>

        <el-form ref="formRef" :model="form" :rules="rules" label-position="top" class="login-form">
          <el-form-item label="用户名" prop="username">
            <el-input v-model="form.username" placeholder="请输入用户名" prefix-icon="User" size="large" />
          </el-form-item>

          <el-form-item v-if="isRegister" label="邮箱" prop="email">
            <el-input v-model="form.email" placeholder="请输入邮箱" prefix-icon="Message" size="large" />
          </el-form-item>

          <el-form-item label="密码" prop="password">
            <el-input v-model="form.password" type="password" placeholder="请输入密码" prefix-icon="Lock" size="large" show-password />
          </el-form-item>

          <el-form-item v-if="isRegister" label="角色" prop="role">
            <el-select v-model="form.role" placeholder="选择角色" size="large" style="width: 100%">
              <el-option label="普通用户" value="user" />
              <el-option label="商家" value="merchant" />
            </el-select>
          </el-form-item>

          <el-form-item>
            <el-button type="primary" size="large" :loading="loading" @click="handleSubmit" style="width: 100%; height: 46px; font-size: 16px; border-radius: 10px;">
              {{ isRegister ? '注 册' : '登 录' }}
            </el-button>
          </el-form-item>
        </el-form>

        <div class="toggle-mode">
          <span>{{ isRegister ? '已有账号？' : '没有账号？' }}</span>
          <el-link type="primary" @click="isRegister = !isRegister">
            {{ isRegister ? '去登录' : '去注册' }}
          </el-link>
        </div>

        <div v-if="!isRegister" class="demo-accounts">
          <p>演示账号：</p>
          <div class="demo-btns">
            <el-button size="small" round @click="fillDemo('admin', 'admin123')">管理员</el-button>
            <el-button size="small" round @click="fillDemo('merchant1', '123456')">商家</el-button>
            <el-button size="small" round @click="fillDemo('user1', '123456')">用户</el-button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { authApi } from '@/api'

const router = useRouter()
const formRef = ref(null)
const isRegister = ref(false)
const loading = ref(false)

const form = reactive({
  username: '',
  password: '',
  email: '',
  role: 'user',
})

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
  email: [{ required: true, message: '请输入邮箱', trigger: 'blur' }],
}

const fillDemo = (username, password) => {
  form.username = username
  form.password = password
}

const handleSubmit = async () => {
  try {
    await formRef.value.validate()
  } catch { return }

  loading.value = true
  try {
    if (isRegister.value) {
      await authApi.register(form)
      ElMessage.success('注册成功，请登录')
      isRegister.value = false
    } else {
      const res = await authApi.login({ username: form.username, password: form.password })
      localStorage.setItem('token', res.data.token)
      localStorage.setItem('user', JSON.stringify(res.data.user))
      ElMessage.success('登录成功')
      router.push('/dashboard')
    }
  } finally {
    loading.value = false
  }
}
</script>

<style lang="scss" scoped>
.login-page {
  height: 100vh;
  display: flex;
  overflow: hidden;
}

.login-left {
  flex: 1;
  background: linear-gradient(135deg, #1a4d32 0%, #2d8c5a 50%, #3aaf6e 100%);
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 60px;

  .brand-area {
    margin-bottom: 48px;

    .brand-icon-wrap {
      width: 64px;
      height: 64px;
      background: rgba(255,255,255,0.15);
      border-radius: 16px;
      display: flex;
      align-items: center;
      justify-content: center;
      margin-bottom: 20px;
    }

    h1 {
      font-size: 32px;
      font-weight: 700;
      color: #fff;
      margin-bottom: 12px;
    }

    p {
      font-size: 16px;
      color: rgba(255, 255, 255, 0.75);
      line-height: 1.6;
    }
  }

  .feature-list {
    display: flex;
    flex-direction: column;
    gap: 20px;

    .feature-item {
      display: flex;
      align-items: center;
      gap: 14px;
      padding: 14px 20px;
      background: rgba(255, 255, 255, 0.08);
      border-radius: 12px;
      backdrop-filter: blur(8px);
      transition: background 0.3s;

      &:hover { background: rgba(255, 255, 255, 0.14); }

      span {
        font-size: 15px;
        color: rgba(255, 255, 255, 0.9);
        font-weight: 500;
      }
    }
  }
}

.login-right {
  width: 480px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-white);
  padding: 40px;

  .login-card {
    width: 100%;
    max-width: 380px;

    h2 {
      font-size: 26px;
      font-weight: 700;
      color: var(--text-primary);
      margin-bottom: 8px;
    }

    .subtitle {
      font-size: 14px;
      color: var(--text-muted);
      margin-bottom: 32px;
    }

    .login-form {
      :deep(.el-form-item__label) {
        font-weight: 500;
        color: var(--text-secondary);
      }

      :deep(.el-input__wrapper) {
        border-radius: 10px;
        box-shadow: 0 0 0 1px var(--border-color) inset;

        &:focus-within {
          box-shadow: 0 0 0 1px var(--primary-color) inset !important;
        }
      }
    }

    .toggle-mode {
      text-align: center;
      margin-top: 16px;
      font-size: 14px;
      color: var(--text-muted);
    }

    .demo-accounts {
      margin-top: 24px;
      padding-top: 20px;
      border-top: 1px dashed var(--border-color);

      p {
        font-size: 13px;
        color: var(--text-muted);
        margin-bottom: 10px;
      }

      .demo-btns {
        display: flex;
        gap: 8px;
      }
    }
  }
}
</style>
