<template>
  <div class="users-page">
    <div class="page-header">
      <h2>用户管理</h2>
      <p>管理系统用户账号</p>
    </div>

    <el-card>
      <div style="display: flex; gap: 12px; margin-bottom: 20px;">
        <el-input v-model="searchKeyword" placeholder="搜索用户名/昵称/邮箱" prefix-icon="Search" style="width: 260px;" clearable @clear="loadUsers" @keyup.enter="loadUsers" />
        <el-select v-model="searchRole" placeholder="全部角色" clearable @change="loadUsers" style="width: 130px;">
          <el-option label="管理员" value="admin" />
          <el-option label="商家" value="merchant" />
          <el-option label="普通用户" value="user" />
        </el-select>
        <el-button type="primary" @click="loadUsers">查询</el-button>
      </div>

      <el-table :data="users" v-loading="loading" stripe>
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column label="头像" width="70">
          <template #default="{ row }">
            <el-avatar :size="36" :src="row.avatar || ''">
              {{ row.nickname?.charAt(0) || 'U' }}
            </el-avatar>
          </template>
        </el-table-column>
        <el-table-column prop="username" label="用户名" width="130" />
        <el-table-column prop="nickname" label="昵称" width="160" />
        <el-table-column prop="email" label="邮箱" min-width="200" />
        <el-table-column label="角色" width="100">
          <template #default="{ row }">
            <el-tag :type="getRoleType(row.role)" size="small">{{ getRoleText(row.role) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="80">
          <template #default="{ row }">
            <el-switch v-model="row.status" :active-value="1" :inactive-value="0" @change="updateStatus(row)" />
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="注册时间" width="160" />
        <el-table-column label="操作" width="100" fixed="right">
          <template #default="{ row }">
            <el-popconfirm v-if="row.role !== 'admin'" title="确定删除此用户?" @confirm="deleteUser(row.id)">
              <template #reference>
                <el-button type="danger" size="small" link>删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-if="total > 0"
        style="margin-top: 20px; justify-content: flex-end;"
        :current-page="page"
        :page-size="pageSize"
        :total="total"
        layout="total, prev, pager, next"
        @current-change="(p) => { page = p; loadUsers() }"
      />
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { userApi } from '@/api'

const users = ref([])
const loading = ref(false)
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)
const searchKeyword = ref('')
const searchRole = ref('')

const getRoleType = (r) => ({ admin: 'danger', merchant: 'warning', user: '' }[r] || '')
const getRoleText = (r) => ({ admin: '管理员', merchant: '商家', user: '用户' }[r] || r)

const loadUsers = async () => {
  loading.value = true
  try {
    const res = await userApi.getUsers({ page: page.value, per_page: pageSize.value, keyword: searchKeyword.value, role: searchRole.value })
    users.value = res.data.items
    total.value = res.data.total
  } finally { loading.value = false }
}

const updateStatus = async (user) => {
  await userApi.updateUser(user.id, { status: user.status })
  ElMessage.success('状态已更新')
}

const deleteUser = async (id) => {
  await userApi.deleteUser(id)
  ElMessage.success('删除成功')
  loadUsers()
}

onMounted(loadUsers)
</script>
