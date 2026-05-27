<template>
  <div class="demand-page">
    <div class="page-header">
      <h2>需求挖掘</h2>
      <p>基于 LDA 主题模型挖掘用户核心需求</p>
    </div>

    <el-row :gutter="20">
      <el-col :span="8">
        <el-card>
          <template #header><span style="font-weight: 600;">挖掘设置</span></template>
          <el-form label-position="top">
            <el-form-item label="选择商品">
              <el-select v-model="selectedProduct" filterable placeholder="搜索并选择商品" style="width: 100%;" @change="onProductChange">
                <el-option v-for="p in products" :key="p.id" :label="p.name" :value="p.id" />
              </el-select>
            </el-form-item>
            <el-form-item label="主题数量">
              <el-slider v-model="numTopics" :min="3" :max="10" :step="1" show-stops />
            </el-form-item>
            <el-button type="primary" :loading="analyzing" @click="runDemand" style="width: 100%;" :disabled="!selectedProduct">
              开始挖掘
            </el-button>
          </el-form>
        </el-card>

        <el-card v-if="topics.length" style="margin-top: 20px;">
          <template #header><span style="font-weight: 600;">主题列表</span></template>
          <div v-for="topic in topics" :key="topic.id" class="topic-item">
            <div class="topic-header">
              <el-tag type="success" size="small">{{ topic.topic_name }}</el-tag>
              <span class="topic-weight">权重: {{ topic.weight }}</span>
            </div>
            <div class="topic-words">
              <el-tag v-for="w in parseWords(topic.topic_words)" :key="w" size="small" effect="plain" style="margin: 2px;">
                {{ w }}
              </el-tag>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="16">
        <el-card v-if="keywords.length">
          <template #header><span style="font-weight: 600;">关键词词云</span></template>
          <div ref="wordCloudRef" style="height: 400px;"></div>
        </el-card>

        <el-card v-if="topics.length" style="margin-top: 20px;">
          <template #header><span style="font-weight: 600;">主题权重分布</span></template>
          <div ref="topicChartRef" style="height: 300px;"></div>
        </el-card>

        <el-card v-if="keywords.length" style="margin-top: 20px;">
          <template #header><span style="font-weight: 600;">高频关键词 Top 20</span></template>
          <div ref="barChartRef" style="height: 350px;"></div>
        </el-card>

        <el-empty v-if="!topics.length && !keywords.length" description="请选择商品并运行需求挖掘" :image-size="120" />
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, nextTick } from 'vue'
import * as echarts from 'echarts'
import 'echarts-wordcloud'
import { ElMessage } from 'element-plus'
import { reviewApi, analysisApi } from '@/api'

const products = ref([])
const selectedProduct = ref(null)
const numTopics = ref(5)
const analyzing = ref(false)
const topics = ref([])
const keywords = ref([])
const wordCloudRef = ref(null)
const topicChartRef = ref(null)
const barChartRef = ref(null)
const chartInstances = []

const parseWords = (str) => { try { return JSON.parse(str) } catch { return [] } }

const createChart = (domRef) => {
  if (!domRef) return null
  const inst = echarts.init(domRef)
  chartInstances.push(inst)
  return inst
}

const disposeCharts = () => {
  chartInstances.forEach(c => c.dispose())
  chartInstances.length = 0
}

const loadProducts = async () => {
  try {
    const res = await reviewApi.getProducts({ per_page: 100 })
    products.value = res.data.items || []
  } catch (e) {
    ElMessage.error('加载商品列表失败')
  }
}

const onProductChange = () => {
  topics.value = []
  keywords.value = []
  disposeCharts()
}

const loadResults = async () => {
  if (!selectedProduct.value) return
  try {
    const res = await analysisApi.getDemandResults({ product_id: selectedProduct.value })
    topics.value = res.data.topics || []
    keywords.value = res.data.keywords || []
    await nextTick()
    initCharts()
  } catch {
    topics.value = []
    keywords.value = []
  }
}

const runDemand = async () => {
  analyzing.value = true
  try {
    await analysisApi.runDemand({ product_id: selectedProduct.value, num_topics: numTopics.value })
    ElMessage.success('需求挖掘完成')
    await loadResults()
  } finally { analyzing.value = false }
}

const initCharts = () => {
  disposeCharts()

  if (keywords.value.length) {
    const cloud = createChart(wordCloudRef.value)
    if (cloud) {
      cloud.setOption({
        series: [{
          type: 'wordCloud',
          shape: 'circle',
          sizeRange: [14, 60],
          rotationRange: [-30, 30],
          gridSize: 8,
          textStyle: {
            fontFamily: 'PingFang SC, Microsoft YaHei, sans-serif',
            color: () => {
              const colors = ['#2d8c5a', '#4aad7a', '#e8a838', '#5b8def', '#e86a6a', '#8b5cf6', '#06b6d4']
              return colors[Math.floor(Math.random() * colors.length)]
            },
          },
          data: keywords.value.slice(0, 30).map(k => ({
            name: k.keyword,
            value: k.frequency,
          })),
        }],
      })
    }
  }

  if (topics.value.length) {
    const topicChart = createChart(topicChartRef.value)
    if (topicChart) {
      topicChart.setOption({
        tooltip: { trigger: 'item' },
        color: ['#2d8c5a', '#4aad7a', '#e8a838', '#5b8def', '#e86a6a', '#8b5cf6', '#06b6d4', '#f59e0b'],
        series: [{
          type: 'pie', radius: ['30%', '65%'],
          roseType: 'area',
          itemStyle: { borderRadius: 6 },
          data: topics.value.map(t => ({ value: t.weight, name: t.topic_name })),
        }],
      })
    }
  }

  if (keywords.value.length) {
    const barChart = createChart(barChartRef.value)
    if (barChart) {
      const top20 = keywords.value.slice(0, 20).reverse()
      barChart.setOption({
        tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
        grid: { left: 80, right: 30, top: 10, bottom: 30 },
        xAxis: { type: 'value' },
        yAxis: { type: 'category', data: top20.map(k => k.keyword) },
        color: ['#2d8c5a'],
        series: [{
          type: 'bar', data: top20.map(k => k.frequency),
          barWidth: 16,
          itemStyle: { borderRadius: [0, 6, 6, 0] },
        }],
      })
    }
  }
}

const handleResize = () => chartInstances.forEach(c => c.resize())

onMounted(() => {
  loadProducts()
  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  disposeCharts()
  window.removeEventListener('resize', handleResize)
})
</script>

<style lang="scss" scoped>
.topic-item {
  padding: 12px 0;
  border-bottom: 1px solid var(--border-light);

  &:last-child { border-bottom: none; }

  .topic-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 8px;

    .topic-weight { font-size: 12px; color: var(--text-muted); }
  }

  .topic-words {
    display: flex;
    flex-wrap: wrap;
    gap: 4px;
  }
}
</style>
