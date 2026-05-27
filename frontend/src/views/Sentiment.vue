<template>
  <div class="sentiment-page">
    <div class="page-header">
      <h2>情感分析</h2>
      <p>基于 SnowNLP / BERT 对商品评论进行情感分析</p>
    </div>

    <el-row :gutter="20">
      <el-col :span="8">
        <el-card>
          <template #header><span style="font-weight: 600;">分析设置</span></template>
          <el-form label-position="top">
            <el-form-item label="选择商品">
              <el-select v-model="selectedProduct" filterable placeholder="搜索并选择商品" style="width: 100%;" @change="onProductChange">
                <el-option v-for="p in products" :key="p.id" :label="p.name" :value="p.id">
                  <span>{{ p.name }}</span>
                  <span style="float:right;color:#8c8c8c;font-size:12px;">{{ p.review_count }}条评论</span>
                </el-option>
              </el-select>
            </el-form-item>
            <el-form-item label="分析算法">
              <el-radio-group v-model="algorithm">
                <el-radio value="snownlp">SnowNLP</el-radio>
                <el-radio value="bert">BERT</el-radio>
              </el-radio-group>
            </el-form-item>
            <el-button type="primary" :loading="analyzing" @click="runAnalysis" style="width: 100%;" :disabled="!selectedProduct">
              开始分析
            </el-button>
          </el-form>

          <div v-if="summary" class="summary-info" style="margin-top: 24px;">
            <h4 style="margin-bottom: 12px; color: var(--text-primary);">分析摘要</h4>
            <div class="info-row"><span>评论总数</span><strong>{{ summary.total_reviews }}</strong></div>
            <div class="info-row"><span>平均情感分</span><strong>{{ summary.avg_score }}</strong></div>
            <div class="info-row"><span>正面占比</span><strong style="color:#52c41a;">{{ summary.positive_ratio }}%</strong></div>
            <div class="info-row"><span>负面占比</span><strong style="color:#f5222d;">{{ summary.negative_ratio }}%</strong></div>
            <div class="info-row"><span>中性占比</span><strong style="color:#8c8c8c;">{{ summary.neutral_ratio }}%</strong></div>
            <div class="info-row"><span>分析算法</span><strong>{{ summary.algorithm }}</strong></div>
            <div class="info-row"><span>分析时间</span><strong>{{ summary.analyzed_at }}</strong></div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="16">
        <el-card v-if="summary">
          <template #header><span style="font-weight: 600;">情感分布饼图</span></template>
          <div ref="pieChartRef" style="height: 350px;"></div>
        </el-card>

        <el-card v-if="reviewSentiments.length" style="margin-top: 20px;">
          <template #header><span style="font-weight: 600;">评论情感详情</span></template>
          <div ref="scatterChartRef" style="height: 300px;"></div>
        </el-card>

        <el-card v-if="reviewSentiments.length" style="margin-top: 20px;">
          <template #header><span style="font-weight: 600;">评论列表</span></template>
          <el-table :data="reviewSentiments" stripe size="small" max-height="400">
            <el-table-column prop="content" label="评论内容" min-width="250" show-overflow-tooltip />
            <el-table-column label="情感分值" width="110">
              <template #default="{ row }">
                <el-progress :percentage="Math.round((row.sentiment_score || 0) * 100)" :color="getScoreColor(row.sentiment_score)" :stroke-width="8" />
              </template>
            </el-table-column>
            <el-table-column label="情感标签" width="100">
              <template #default="{ row }">
                <el-tag :type="getSentimentType(row.sentiment_label)" size="small" round>
                  {{ getSentimentText(row.sentiment_label) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="rating" label="评分" width="70" />
          </el-table>
        </el-card>

        <el-empty v-if="!summary" description="请选择商品并运行分析" :image-size="120" />
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, nextTick } from 'vue'
import * as echarts from 'echarts'
import { ElMessage } from 'element-plus'
import { reviewApi, analysisApi } from '@/api'

const products = ref([])
const selectedProduct = ref(null)
const algorithm = ref('snownlp')
const analyzing = ref(false)
const summary = ref(null)
const reviewSentiments = ref([])
const pieChartRef = ref(null)
const scatterChartRef = ref(null)
const chartInstances = []

const getSentimentType = (l) => ({ positive: 'success', negative: 'danger', neutral: 'info' }[l] || 'info')
const getSentimentText = (l) => ({ positive: '正面', negative: '负面', neutral: '中性' }[l] || '-')
const getScoreColor = (s) => s >= 0.6 ? '#52c41a' : s <= 0.4 ? '#f5222d' : '#faad14'

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
  summary.value = null
  reviewSentiments.value = []
  disposeCharts()
}

const loadDetail = async () => {
  if (!selectedProduct.value) return
  try {
    const res = await analysisApi.getSentimentDetail(selectedProduct.value)
    summary.value = res.data.summary
    reviewSentiments.value = res.data.reviews || []
    await nextTick()
    initCharts()
  } catch {
    summary.value = null
    reviewSentiments.value = []
  }
}

const runAnalysis = async () => {
  analyzing.value = true
  try {
    await analysisApi.runSentiment({ product_id: selectedProduct.value, algorithm: algorithm.value })
    ElMessage.success('分析完成')
    await loadDetail()
  } finally { analyzing.value = false }
}

const initCharts = () => {
  if (!summary.value) return
  disposeCharts()

  const pie = createChart(pieChartRef.value)
  if (pie) {
    pie.setOption({
      tooltip: { trigger: 'item' },
      legend: { bottom: 10 },
      color: ['#52c41a', '#f5222d', '#d9d9d9'],
      series: [{
        type: 'pie', radius: ['45%', '72%'],
        itemStyle: { borderRadius: 8, borderColor: '#fff', borderWidth: 3 },
        label: { formatter: '{b}\n{c}条 ({d}%)' },
        data: [
          { value: summary.value.positive_count, name: '正面' },
          { value: summary.value.negative_count, name: '负面' },
          { value: summary.value.neutral_count, name: '中性' },
        ],
      }],
    })
  }

  if (reviewSentiments.value.length) {
    const scatter = createChart(scatterChartRef.value)
    if (scatter) {
      scatter.setOption({
        tooltip: { trigger: 'item', formatter: (p) => `评论${p.dataIndex + 1}<br/>情感分: ${p.data[1].toFixed(3)}<br/>评分: ${p.data[0]}` },
        grid: { left: 50, right: 20, top: 20, bottom: 50 },
        xAxis: { name: '用户评分', type: 'value', min: 0, max: 5 },
        yAxis: { name: '情感分值', type: 'value', min: 0, max: 1 },
        series: [{
          type: 'scatter', symbolSize: 10,
          data: reviewSentiments.value.map(r => [r.rating, r.sentiment_score || 0]),
          itemStyle: {
            color: (p) => {
              const s = p.data[1]
              return s >= 0.6 ? '#52c41a' : s <= 0.4 ? '#f5222d' : '#faad14'
            },
          },
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
.summary-info {
  .info-row {
    display: flex;
    justify-content: space-between;
    padding: 8px 0;
    border-bottom: 1px solid var(--border-light);
    font-size: 13px;

    span { color: var(--text-muted); }
    strong { color: var(--text-primary); }
  }
}
</style>
