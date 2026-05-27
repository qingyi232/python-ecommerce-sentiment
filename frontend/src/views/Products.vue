<template>
  <div class="products-page">
    <div class="page-header">
      <h2>商品管理</h2>
      <p>管理系统中的所有商品信息</p>
    </div>

    <el-card>
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
        <div style="display: flex; gap: 12px;">
          <el-input v-model="searchKeyword" placeholder="搜索商品名称/品牌" prefix-icon="Search" style="width: 260px;" clearable @clear="loadProducts" @keyup.enter="loadProducts" />
          <el-select v-model="searchCategory" placeholder="全部分类" clearable @change="loadProducts" style="width: 140px;">
            <el-option v-for="c in categories" :key="c" :label="c" :value="c" />
          </el-select>
          <el-button type="primary" @click="loadProducts">查询</el-button>
        </div>
        <el-button type="primary" @click="openAddDialog">
          <el-icon><Plus /></el-icon> 添加商品
        </el-button>
      </div>

      <el-table :data="products" v-loading="loading" stripe>
        <el-table-column label="商品图片" width="90">
          <template #default="{ row }">
            <el-image :src="row.image_url" style="width: 60px; height: 60px; border-radius: 8px;" fit="cover">
              <template #error>
                <div style="width:60px;height:60px;background:#f0f5f2;border-radius:8px;display:flex;align-items:center;justify-content:center;color:#aab;font-size:12px;">暂无</div>
              </template>
            </el-image>
          </template>
        </el-table-column>
        <el-table-column prop="name" label="商品名称" min-width="200" show-overflow-tooltip />
        <el-table-column prop="category" label="分类" width="120" />
        <el-table-column prop="brand" label="品牌" width="100" />
        <el-table-column prop="price" label="价格" width="110">
          <template #default="{ row }">¥{{ (row.price || 0).toFixed(2) }}</template>
        </el-table-column>
        <el-table-column prop="review_count" label="评论数" width="90" sortable />
        <el-table-column label="情感均值" width="110">
          <template #default="{ row }">
            <el-tag :type="(row.avg_sentiment || 0) >= 0.6 ? 'success' : (row.avg_sentiment || 0) <= 0.4 ? 'danger' : 'warning'" size="small" round>
              {{ (row.avg_sentiment || 0).toFixed(2) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="source_platform" label="来源" width="80" />
        <el-table-column prop="created_at" label="添加时间" width="160" />
        <el-table-column label="操作" width="140" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" link @click="openEditDialog(row)">编辑</el-button>
            <el-popconfirm title="确定删除此商品及其所有评论?" @confirm="deleteProduct(row.id)">
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
        @current-change="(p) => { page = p; loadProducts() }"
      />
    </el-card>

    <el-dialog v-model="showAddDialog" :title="dialogTitle" width="520px" destroy-on-close>
      <el-form :model="newProduct" label-width="80px">
        <el-form-item label="商品名称">
          <el-input v-model="newProduct.name" placeholder="请输入商品名称" />
        </el-form-item>
        <el-form-item label="分类">
          <el-input v-model="newProduct.category" placeholder="如：手机数码" />
        </el-form-item>
        <el-form-item label="品牌">
          <el-input v-model="newProduct.brand" placeholder="如：华为" />
        </el-form-item>
        <el-form-item label="价格">
          <el-input-number v-model="newProduct.price" :min="0" :precision="2" style="width: 200px;" />
        </el-form-item>
        <el-form-item label="商品图片">
          <div style="display: flex; flex-direction: column; gap: 10px; width: 100%;">
            <el-radio-group v-model="imageMode" size="small">
              <el-radio-button value="upload">本地上传</el-radio-button>
              <el-radio-button value="url">在线URL</el-radio-button>
            </el-radio-group>
            <el-upload
              v-if="imageMode === 'upload'"
              :auto-upload="false"
              :show-file-list="false"
              :on-change="handleFileChange"
              accept="image/*"
            >
              <div v-if="previewUrl" style="position: relative;">
                <el-image :src="previewUrl" style="width: 120px; height: 120px; border-radius: 8px;" fit="cover" />
                <el-button size="small" type="danger" circle style="position: absolute; top: -8px; right: -8px;" @click.stop="clearImage">
                  <el-icon><Close /></el-icon>
                </el-button>
              </div>
              <div v-else style="width: 120px; height: 120px; border: 2px dashed #d9e5dc; border-radius: 8px; display: flex; flex-direction: column; align-items: center; justify-content: center; cursor: pointer; color: #8c998e;">
                <el-icon :size="28"><Plus /></el-icon>
                <span style="font-size: 12px; margin-top: 4px;">点击上传</span>
              </div>
            </el-upload>
            <el-input v-else v-model="newProduct.image_url" placeholder="请输入图片URL地址" />
          </div>
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="newProduct.description" type="textarea" :rows="3" placeholder="商品描述信息" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddDialog = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="addProduct">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { reviewApi, uploadApi } from '@/api'

const products = ref([])
const loading = ref(false)
const submitting = ref(false)
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)
const searchKeyword = ref('')
const searchCategory = ref('')
const categories = ref([])
const showAddDialog = ref(false)
const editingId = ref(null)
const dialogTitle = ref('添加商品')
const imageMode = ref('upload')
const previewUrl = ref('')
const selectedFile = ref(null)

const newProduct = reactive({
  name: '', category: '手机数码', brand: '', price: 0, image_url: '', description: '',
})

const openAddDialog = () => {
  editingId.value = null
  dialogTitle.value = '添加商品'
  Object.assign(newProduct, { name: '', category: '手机数码', brand: '', price: 0, image_url: '', description: '' })
  previewUrl.value = ''
  selectedFile.value = null
  imageMode.value = 'upload'
  showAddDialog.value = true
}

const handleFileChange = (file) => {
  selectedFile.value = file.raw
  previewUrl.value = URL.createObjectURL(file.raw)
}

const clearImage = () => {
  selectedFile.value = null
  previewUrl.value = ''
}

const loadProducts = async () => {
  loading.value = true
  try {
    const res = await reviewApi.getProducts({ page: page.value, per_page: pageSize.value, keyword: searchKeyword.value, category: searchCategory.value })
    products.value = res.data.items
    total.value = res.data.total
  } finally { loading.value = false }
}

const loadCategories = async () => {
  try {
    const res = await reviewApi.getCategories()
    categories.value = res.data || []
  } catch (e) {
    console.warn('加载分类失败:', e?.message)
  }
}

const addProduct = async () => {
  if (!newProduct.name) { ElMessage.warning('请输入商品名称'); return }
  submitting.value = true
  try {
    if (imageMode.value === 'upload' && selectedFile.value) {
      const uploadRes = await uploadApi.uploadImage(selectedFile.value)
      newProduct.image_url = uploadRes.data.url
    }
    if (editingId.value) {
      await reviewApi.updateProduct(editingId.value, { ...newProduct })
      ElMessage.success('更新成功')
    } else {
      await reviewApi.createProduct({ ...newProduct })
      ElMessage.success('添加成功')
    }
    showAddDialog.value = false
    loadProducts()
  } finally { submitting.value = false }
}

const openEditDialog = (row) => {
  editingId.value = row.id
  dialogTitle.value = '编辑商品'
  Object.assign(newProduct, {
    name: row.name,
    category: row.category,
    brand: row.brand,
    price: row.price,
    image_url: row.image_url,
    description: row.description || '',
  })
  previewUrl.value = row.image_url || ''
  selectedFile.value = null
  imageMode.value = row.image_url ? 'url' : 'upload'
  showAddDialog.value = true
}

const deleteProduct = async (id) => {
  await reviewApi.deleteProduct(id)
  ElMessage.success('删除成功')
  loadProducts()
}

onMounted(() => { loadProducts(); loadCategories() })
</script>
