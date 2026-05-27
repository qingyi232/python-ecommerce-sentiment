<template>
  <div class="dashboard">
    <div class="page-header">
      <h2>数据总览</h2>
      <p>实时掌握评论分析系统运行状态</p>
    </div>

    <el-row :gutter="20" class="stat-row">
      <el-col :span="6" v-for="item in statCards" :key="item.label">
        <div class="stat-card" :style="{ borderLeft: `4px solid ${item.color}` }">
          <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
              <div class="stat-value" :style="{ color: item.color }">{{ item.value }}</div>
              <div class="stat-label">{{ item.label }}</div>
            </div>
            <div class="stat-icon" :style="{ background: item.bg }">
              <el-icon :size="24" :color="item.color"><component :is="item.icon" /></el-icon>
            </div>
          </div>
        </div>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="12">
        <el-card>
          <template #header>
            <span style="font-weight: 600;">情感分布</span>
          </template>
          <div ref="sentimentChartRef" style="height: 320px;"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>
            <span style="font-weight: 600;">情感趋势</span>
          </template>
          <div ref="trendChartRef" style="height: 320px;"></div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="12">
        <el-card>
          <template #header>
            <span style="font-weight: 600;">商品分类统计</span>
          </template>
          <div ref="categoryChartRef" style="height: 320px;"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>
            <span style="font-weight: 600;">最新评论</span>
          </template>
          <div class="recent-reviews">
            <div v-for="review in recentReviews" :key="review.id" class="review-item">
              <div class="review-header">
                <span class="reviewer">{{ review.reviewer_name }}</span>
                <el-tag :type="getSentimentType(review.sentiment_label)" size="small" round>
                  {{ getSentimentText(review.sentiment_label) }}
                </el-tag>
              </div>
              <div class="review-content">{{ review.content }}</div>
              <div class="review-meta">
                <span>{{ review.product_name }}</span>
                <span>{{ review.created_at }}</span>
              </div>
            </div>
            <el-empty v-if="!recentReviews.length" description="暂无评论" :image-size="80" />
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, computed, nextTick } from 'vue'
import * as echarts from 'echarts'
import { dashboardApi } from '@/api'
import { ElMessage } from 'element-plus'

const stats = ref({})
const recentReviews = ref([])
const categoryStats = ref([])
const trendData = ref([])

const sentimentChartRef = ref(null)
const trendChartRef = ref(null)
const categoryChartRef = ref(null)

const chartInstances = []

const statCards = computed(() => [
  { label: '商品总数', value: stats.value.total_products || 0, icon: 'Goods', color: '#2d8c5a', bg: '#e8f5ee' },
  { label: '评论总数', value: stats.value.total_reviews || 0, icon: 'ChatDotSquare', color: '#e8a838', bg: '#fef6e8' },
  { label: '已分析', value: stats.value.analyzed_reviews || 0, icon: 'TrendCharts', color: '#5b8def', bg: '#edf2fd' },
  { label: '用户数', value: stats.value.total_users || 0, icon: 'User', color: '#e86a6a', bg: '#fdeaea' },
])

const getSentimentType = (label) => ({ positive: 'success', negative: 'danger', neutral: 'info' }[label] || 'info')
const getSentimentText = (label) => ({ positive: '正面', negative: '负面', neutral: '中性' }[label] || '未分析')

const createChart = (domRef) => {
  if (!domRef) return null
  const instance = echarts.init(domRef)
  chartInstances.push(instance)
  return instance
}

const initSentimentChart = () => {
  const chart = createChart(sentimentChartRef.value)
  if (!chart) return
  const dist = stats.value.sentiment_distribution || {}
  chart.setOption({
    tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
    legend: { bottom: 10 },
    color: ['#52c41a', '#f5222d', '#8c8c8c'],
    series: [{
      type: 'pie',
      radius: ['40%', '70%'],
      avoidLabelOverlap: true,
      itemStyle: { borderRadius: 8, borderColor: '#fff', borderWidth: 3 },
      label: { show: true, formatter: '{b}\n{d}%' },
      data: [
        { value: dist.positive || 0, name: '正面评价' },
        { value: dist.negative || 0, name: '负面评价' },
        { value: dist.neutral || 0, name: '中性评价' },
      ],
    }],
  })
}

const initTrendChart = () => {
  const chart = createChart(trendChartRef.value)
  if (!chart) return
  chart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['正面', '负面', '中性'], bottom: 10 },
    grid: { left: 40, right: 20, top: 20, bottom: 60 },
    xAxis: { type: 'category', data: trendData.value.map(d => d.date), axisLabel: { rotate: 30 } },
    yAxis: { type: 'value' },
    color: ['#52c41a', '#f5222d', '#8c8c8c'],
    series: [
      { name: '正面', type: 'line', smooth: true, data: trendData.value.map(d => d.positive), areaStyle: { opacity: 0.1 } },
      { name: '负面', type: 'line', smooth: true, data: trendData.value.map(d => d.negative), areaStyle: { opacity: 0.1 } },
      { name: '中性', type: 'line', smooth: true, data: trendData.value.map(d => d.neutral), areaStyle: { opacity: 0.1 } },
    ],
  })
}

const initCategoryChart = () => {
  const chart = createChart(categoryChartRef.value)
  if (!chart) return
  chart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { left: 80, right: 20, top: 20, bottom: 40 },
    xAxis: { type: 'value' },
    yAxis: { type: 'category', data: categoryStats.value.map(c => c.category) },
    color: ['#2d8c5a'],
    series: [{
      type: 'bar',
      data: categoryStats.value.map(c => c.review_count),
      barWidth: 20,
      itemStyle: { borderRadius: [0, 6, 6, 0] },
    }],
  })
}

const handleResize = () => chartInstances.forEach(c => c.resize())

onMounted(async () => {
  try {
    const [statsRes, reviewsRes, categoryRes, trendRes] = await Promise.all([
      dashboardApi.getStats(),
      dashboardApi.getRecentReviews(),
      dashboardApi.getCategoryStats(),
      dashboardApi.getSentimentTrend(),
    ])
    stats.value = statsRes.data
    recentReviews.value = reviewsRes.data || []
    categoryStats.value = categoryRes.data || []
    trendData.value = trendRes.data || []

    await nextTick()
    initSentimentChart()
    initTrendChart()
    initCategoryChart()
    window.addEventListener('resize', handleResize)
  } catch (e) {
    ElMessage.error('加载仪表盘数据失败')
  }
})

onBeforeUnmount(() => {
  chartInstances.forEach(c => c.dispose())
  chartInstances.length = 0
  window.removeEventListener('resize', handleResize)
})
</script>

<style lang="scss" scoped>
.stat-row {
  .stat-card {
    background: var(--bg-white);
    padding: 24px;
    border-radius: var(--radius-md);
    border: 1px solid var(--border-light);
    transition: all 0.3s;

    &:hover {
      transform: translateY(-3px);
      box-shadow: var(--shadow-md);
    }
  }
}

.recent-reviews {
  max-height: 280px;
  overflow-y: auto;

  .review-item {
    padding: 12px 0;
    border-bottom: 1px solid var(--border-light);

    &:last-child { border-bottom: none; }

    .review-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 6px;

      .reviewer {
        font-weight: 500;
        font-size: 13px;
        color: var(--text-primary);
      }
    }

    .review-content {
      font-size: 13px;
      color: var(--text-secondary);
      line-height: 1.5;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }

    .review-meta {
      display: flex;
      justify-content: space-between;
      margin-top: 6px;
      font-size: 12px;
      color: var(--text-muted);
    }
  }
}
</style>
