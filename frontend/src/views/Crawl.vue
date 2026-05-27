<template>
  <div class="crawl-page">
    <div class="page-header">
      <h2>数据采集</h2>
      <p>管理评论数据爬取任务</p>
    </div>

    <el-card>
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
        <el-select v-model="filterStatus" placeholder="全部状态" clearable @change="loadTasks" style="width: 140px;">
          <el-option label="待执行" value="pending" />
          <el-option label="执行中" value="running" />
          <el-option label="已完成" value="completed" />
          <el-option label="失败" value="failed" />
        </el-select>
        <el-button type="primary" @click="showCreateDialog = true">
          <el-icon><Plus /></el-icon> 新建任务
        </el-button>
      </div>

      <el-table :data="tasks" v-loading="loading" stripe>
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column prop="task_name" label="任务名称" min-width="200" />
        <el-table-column prop="platform" label="平台" width="80" />
        <el-table-column prop="keyword" label="关键词" width="140" />
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small">{{ getStatusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="success_count" label="成功数" width="80" />
        <el-table-column prop="fail_count" label="失败数" width="80" />
        <el-table-column prop="creator_name" label="创建者" width="100" />
        <el-table-column prop="created_at" label="创建时间" width="160" />
        <el-table-column label="操作" width="160" fixed="right">
          <template #default="{ row }">
            <el-button v-if="row.status === 'pending'" type="primary" size="small" link @click="startTask(row.id)">启动</el-button>
            <el-popconfirm title="确定删除此任务?" @confirm="deleteTask(row.id)">
              <template #reference>
                <el-button type="danger" size="small" link :disabled="row.status === 'running'">删除</el-button>
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
        @current-change="(p) => { page = p; loadTasks() }"
      />
    </el-card>

    <el-dialog v-model="showCreateDialog" title="新建采集任务" width="480px">
      <el-form :model="newTask" label-width="80px">
        <el-form-item label="任务名称"><el-input v-model="newTask.task_name" placeholder="如：华为手机评论采集" /></el-form-item>
        <el-form-item label="目标平台">
          <el-select v-model="newTask.platform" style="width: 100%;">
            <el-option label="京东" value="京东" />
            <el-option label="淘宝" value="淘宝" />
            <el-option label="天猫" value="天猫" />
          </el-select>
        </el-form-item>
        <el-form-item label="搜索关键词"><el-input v-model="newTask.keyword" placeholder="如：华为Mate60" /></el-form-item>
        <el-form-item label="目标URL"><el-input v-model="newTask.target_url" placeholder="可选，指定商品页URL" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="createTask">创建</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { crawlApi } from '@/api'

const tasks = ref([])
const loading = ref(false)
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)
const filterStatus = ref('')
const showCreateDialog = ref(false)
const newTask = reactive({ task_name: '', platform: '京东', keyword: '', target_url: '' })

const getStatusType = (s) => ({ pending: 'info', running: 'warning', completed: 'success', failed: 'danger' }[s] || 'info')
const getStatusText = (s) => ({ pending: '待执行', running: '执行中', completed: '已完成', failed: '失败' }[s] || s)

const loadTasks = async () => {
  loading.value = true
  try {
    const res = await crawlApi.getTasks({ page: page.value, per_page: pageSize.value, status: filterStatus.value })
    tasks.value = res.data.items
    total.value = res.data.total
  } finally { loading.value = false }
}

const createTask = async () => {
  if (!newTask.task_name) { ElMessage.warning('请输入任务名称'); return }
  await crawlApi.createTask(newTask)
  ElMessage.success('任务创建成功')
  showCreateDialog.value = false
  loadTasks()
}

const startTask = async (id) => {
  await crawlApi.startTask(id)
  ElMessage.success('任务已启动')
  loadTasks()
}

const deleteTask = async (id) => {
  await crawlApi.deleteTask(id)
  ElMessage.success('删除成功')
  loadTasks()
}

onMounted(loadTasks)
</script>
