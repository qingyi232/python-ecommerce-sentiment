<template>
  <div class="reviews-page">
    <div class="page-header">
      <h2>评论管理</h2>
      <p>查看和管理所有商品评论数据</p>
    </div>

    <el-card>
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
        <div style="display: flex; gap: 12px;">
          <el-input v-model="searchKeyword" placeholder="搜索评论内容" prefix-icon="Search" style="width: 240px;" clearable @clear="loadReviews" @keyup.enter="loadReviews" />
          <el-select v-model="searchSentiment" placeholder="情感类型" clearable @change="loadReviews" style="width: 130px;">
            <el-option label="正面" value="positive" />
            <el-option label="负面" value="negative" />
            <el-option label="中性" value="neutral" />
          </el-select>
          <el-button type="primary" @click="loadReviews">查询</el-button>
        </div>
      </div>

      <el-table :data="reviews" v-loading="loading" stripe>
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column prop="product_name" label="所属商品" width="200" show-overflow-tooltip />
        <el-table-column prop="content" label="评论内容" min-width="300" show-overflow-tooltip />
        <el-table-column prop="reviewer_name" label="评论者" width="110" />
        <el-table-column label="评分" width="90">
          <template #default="{ row }">
            <el-rate v-model="row.rating" disabled :max="5" size="small" />
          </template>
        </el-table-column>
        <el-table-column label="情感" width="100">
          <template #default="{ row }">
            <el-tag v-if="row.sentiment_label" :type="getSentimentType(row.sentiment_label)" size="small" round>
              {{ getSentimentText(row.sentiment_label) }}
            </el-tag>
            <span v-else style="color: var(--text-muted); font-size: 12px;">未分析</span>
          </template>
        </el-table-column>
        <el-table-column label="情感分值" width="100">
          <template #default="{ row }">
            <span v-if="row.sentiment_score !== null">{{ row.sentiment_score?.toFixed(3) }}</span>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="source_platform" label="来源" width="80" />
        <el-table-column prop="review_time" label="评论时间" width="160" />
        <el-table-column label="操作" width="80" fixed="right">
          <template #default="{ row }">
            <el-popconfirm title="确定删除此评论?" @confirm="deleteReview(row.id)">
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
        @current-change="(p) => { page = p; loadReviews() }"
      />
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { reviewApi } from '@/api'

const reviews = ref([])
const loading = ref(false)
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)
const searchKeyword = ref('')
const searchSentiment = ref('')

const getSentimentType = (label) => ({ positive: 'success', negative: 'danger', neutral: 'info' }[label] || 'info')
const getSentimentText = (label) => ({ positive: '正面', negative: '负面', neutral: '中性' }[label] || '未知')

const loadReviews = async () => {
  loading.value = true
  try {
    const res = await reviewApi.getReviews({ page: page.value, per_page: pageSize.value, keyword: searchKeyword.value, sentiment: searchSentiment.value })
    reviews.value = res.data.items
    total.value = res.data.total
  } finally { loading.value = false }
}

const deleteReview = async (id) => {
  await reviewApi.deleteReview(id)
  ElMessage.success('删除成功')
  loadReviews()
}

onMounted(() => { loadReviews() })
</script>
