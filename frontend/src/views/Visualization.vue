<template>
  <div class="visualization-page">
    <div class="page-header">
      <h2>可视化展示</h2>
      <p>多维度可视化展示分析结果</p>
    </div>

    <div style="margin-bottom: 20px; display: flex; gap: 12px; align-items: center;">
      <el-select v-model="selectedProduct" filterable placeholder="选择商品查看详情" style="width: 300px;" @change="loadData">
        <el-option v-for="p in products" :key="p.id" :label="p.name" :value="p.id" />
      </el-select>
      <el-tag v-if="loading" type="info">加载中...</el-tag>
      <el-tag v-if="errorMsg" type="danger">{{ errorMsg }}</el-tag>
    </div>

    <template v-if="selectedProduct && sentimentData">
      <el-row :gutter="20">
        <el-col :span="12">
          <el-card>
            <template #header><span style="font-weight: 600;">情感分布 - 环形图</span></template>
            <div ref="donutRef" style="height: 380px;"></div>
          </el-card>
        </el-col>
        <el-col :span="12">
          <el-card>
            <template #header><span style="font-weight: 600;">评分分布 - 柱状图</span></template>
            <div ref="ratingRef" style="height: 380px;"></div>
          </el-card>
        </el-col>
      </el-row>

      <el-row :gutter="20" style="margin-top: 20px;">
        <el-col :span="12">
          <el-card>
            <template #header><span style="font-weight: 600;">情感分值分布 - 直方图</span></template>
            <div ref="histRef" style="height: 380px;"></div>
          </el-card>
        </el-col>
        <el-col :span="12">
          <el-card>
            <template #header><span style="font-weight: 600;">评分与情感关联 - 散点图</span></template>
            <div ref="correlRef" style="height: 380px;"></div>
          </el-card>
        </el-col>
      </el-row>

      <el-row :gutter="20" style="margin-top: 20px;">
        <el-col :span="24">
          <el-card>
            <template #header><span style="font-weight: 600;">各商品情感对比 - 雷达图</span></template>
            <div ref="radarRef" style="height: 420px;"></div>
          </el-card>
        </el-col>
      </el-row>
    </template>

    <el-empty v-else-if="selectedProduct && !loading && !sentimentData" description="该商品暂无分析数据，请先到「情感分析」页面执行分析" :image-size="120" style="margin-top: 40px;" />
    <el-empty v-else-if="!selectedProduct" description="请选择商品查看可视化分析" :image-size="120" style="margin-top: 40px;" />
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, nextTick } from 'vue'
import * as echarts from 'echarts'
import { reviewApi, analysisApi } from '@/api'
import { ElMessage } from 'element-plus'

const products = ref([])
const selectedProduct = ref(null)
const sentimentData = ref(null)
const reviewsData = ref([])
const loading = ref(false)
const errorMsg = ref('')

const donutRef = ref(null)
const ratingRef = ref(null)
const histRef = ref(null)
const correlRef = ref(null)
const radarRef = ref(null)

const chartInstances = []

const loadProducts = async () => {
  try {
    const res = await reviewApi.getProducts({ per_page: 100 })
    products.value = res.data.items || []
  } catch (e) {
    ElMessage.error('加载商品列表失败')
  }
}

const loadData = async () => {
  if (!selectedProduct.value) return
  loading.value = true
  errorMsg.value = ''
  sentimentData.value = null
  reviewsData.value = []
  disposeCharts()

  try {
    const [sentRes, revRes] = await Promise.all([
      analysisApi.getSentimentDetail(selectedProduct.value),
      reviewApi.getReviews({ product_id: selectedProduct.value, per_page: 200 }),
    ])
    sentimentData.value = sentRes.data.summary
    reviewsData.value = revRes.data.items || []
    await nextTick()
    initAllCharts()
  } catch (e) {
    const msg = e?.response?.data?.message || e?.message || ''
    if (msg.includes('暂无分析结果')) {
      sentimentData.value = null
    } else {
      errorMsg.value = msg || '数据加载失败'
    }
  } finally {
    loading.value = false
  }
}

const disposeCharts = () => {
  chartInstances.forEach(c => c.dispose())
  chartInstances.length = 0
}

const createChart = (domRef) => {
  if (!domRef) return null
  const instance = echarts.init(domRef)
  chartInstances.push(instance)
  return instance
}

const initAllCharts = () => {
  if (!sentimentData.value) return
  disposeCharts()

  const donut = createChart(donutRef.value)
  if (donut) {
    donut.setOption({
      tooltip: { trigger: 'item' },
      legend: { bottom: 10 },
      color: ['#52c41a', '#f5222d', '#bfbfbf'],
      series: [{
        type: 'pie', radius: ['42%', '70%'],
        itemStyle: { borderRadius: 8, borderColor: '#fff', borderWidth: 3 },
        label: { formatter: '{b}\n{d}%', lineHeight: 18 },
        emphasis: { label: { fontSize: 16, fontWeight: 'bold' } },
        data: [
          { value: sentimentData.value.positive_count, name: '正面' },
          { value: sentimentData.value.negative_count, name: '负面' },
          { value: sentimentData.value.neutral_count, name: '中性' },
        ],
      }],
    })
  }

  const ratingDist = [0, 0, 0, 0, 0]
  reviewsData.value.forEach(r => { if (r.rating >= 1 && r.rating <= 5) ratingDist[r.rating - 1]++ })
  const ratingChart = createChart(ratingRef.value)
  if (ratingChart) {
    ratingChart.setOption({
      tooltip: { trigger: 'axis' },
      grid: { left: 50, right: 20, top: 20, bottom: 40 },
      xAxis: { type: 'category', data: ['1星', '2星', '3星', '4星', '5星'] },
      yAxis: { type: 'value' },
      series: [{
        type: 'bar', data: ratingDist, barWidth: 36,
        itemStyle: {
          borderRadius: [6, 6, 0, 0],
          color: (p) => ['#f5222d', '#fa8c16', '#faad14', '#52c41a', '#2d8c5a'][p.dataIndex],
        },
      }],
    })
  }

  const bins = Array(10).fill(0)
  reviewsData.value.forEach(r => {
    if (r.sentiment_score != null) {
      const idx = Math.min(Math.floor(r.sentiment_score * 10), 9)
      bins[idx]++
    }
  })
  const histChart = createChart(histRef.value)
  if (histChart) {
    histChart.setOption({
      tooltip: { trigger: 'axis' },
      grid: { left: 50, right: 20, top: 20, bottom: 40 },
      xAxis: { type: 'category', data: bins.map((_, i) => `${(i / 10).toFixed(1)}-${((i + 1) / 10).toFixed(1)}`) },
      yAxis: { type: 'value' },
      series: [{
        type: 'bar', data: bins, barWidth: 24,
        itemStyle: {
          borderRadius: [4, 4, 0, 0],
          color: (p) => {
            const i = p.dataIndex
            return i < 4 ? '#f5222d' : i < 6 ? '#faad14' : '#52c41a'
          },
        },
      }],
    })
  }

  const scatterData = reviewsData.value
    .filter(r => r.sentiment_score != null)
    .map(r => [r.rating, r.sentiment_score])
  const correlChart = createChart(correlRef.value)
  if (correlChart) {
    correlChart.setOption({
      tooltip: { trigger: 'item' },
      grid: { left: 50, right: 20, top: 20, bottom: 50 },
      xAxis: { name: '用户评分', min: 0, max: 5.5 },
      yAxis: { name: '情感分值', min: 0, max: 1.05 },
      series: [{
        type: 'scatter', symbolSize: 8,
        data: scatterData,
        itemStyle: {
          opacity: 0.7,
          color: (p) => p.data[1] >= 0.6 ? '#52c41a' : p.data[1] <= 0.4 ? '#f5222d' : '#faad14',
        },
      }],
    })
  }

  const topProducts = products.value.slice(0, 6)
  if (topProducts.length > 0) {
    const radarChart = createChart(radarRef.value)
    if (radarChart) {
      const maxReview = Math.max(...topProducts.map(p => p.review_count || 0), 1)
      const maxPrice = Math.max(...topProducts.map(p => p.price || 0), 1)
      radarChart.setOption({
        tooltip: {},
        legend: { data: topProducts.map(p => (p.name || '').substring(0, 10)), bottom: 10, type: 'scroll' },
        radar: {
          indicator: [
            { name: '评论数', max: maxReview + 5 },
            { name: '情感均值', max: 1 },
            { name: '价格(元)', max: Math.ceil(maxPrice / 1000) * 1000 },
          ],
        },
        color: ['#2d8c5a', '#e8a838', '#5b8def', '#e86a6a', '#8b5cf6', '#06b6d4'],
        series: [{
          type: 'radar',
          data: topProducts.map(p => ({
            name: (p.name || '').substring(0, 10),
            value: [
              p.review_count || 0,
              p.avg_sentiment || 0,
              p.price || 0,
            ],
            areaStyle: { opacity: 0.1 },
          })),
        }],
      })
    }
  }
}

const handleResize = () => {
  chartInstances.forEach(c => c.resize())
}

onMounted(() => {
  loadProducts()
  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  disposeCharts()
  window.removeEventListener('resize', handleResize)
})
</script>
