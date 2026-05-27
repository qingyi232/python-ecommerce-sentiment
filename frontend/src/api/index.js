import axios from 'axios'
import { ElMessage } from 'element-plus'
import router from '@/router'

const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
})

api.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  response => {
    const res = response.data
    if (res.code !== 200) {
      ElMessage.error(res.message || '操作失败')
      return Promise.reject(new Error(res.message))
    }
    return res
  },
  error => {
    if (error.response) {
      const { status, data } = error.response
      if (status === 401) {
        localStorage.removeItem('token')
        localStorage.removeItem('user')
        router.push('/login')
        ElMessage.error('登录已过期，请重新登录')
      } else {
        ElMessage.error(data?.message || '请求失败')
      }
    } else {
      ElMessage.error('网络连接失败')
    }
    return Promise.reject(error)
  }
)

export const authApi = {
  login: data => api.post('/auth/login', data),
  register: data => api.post('/auth/register', data),
  getProfile: () => api.get('/auth/profile'),
  updateProfile: data => api.put('/auth/profile', data),
}

export const userApi = {
  getUsers: params => api.get('/users/', { params }),
  updateUser: (id, data) => api.put(`/users/${id}`, data),
  deleteUser: id => api.delete(`/users/${id}`),
}

export const reviewApi = {
  getReviews: params => api.get('/reviews/', { params }),
  getReview: id => api.get(`/reviews/${id}`),
  createReview: data => api.post('/reviews/', data),
  deleteReview: id => api.delete(`/reviews/${id}`),
  getProducts: params => api.get('/reviews/products', { params }),
  getProduct: id => api.get(`/reviews/products/${id}`),
  createProduct: data => api.post('/reviews/products', data),
  updateProduct: (id, data) => api.put(`/reviews/products/${id}`, data),
  deleteProduct: id => api.delete(`/reviews/products/${id}`),
  getCategories: () => api.get('/reviews/categories'),
}

export const analysisApi = {
  runSentiment: data => api.post('/analysis/sentiment/run', data, { timeout: 120000 }),
  getSentimentResults: params => api.get('/analysis/sentiment/results', { params }),
  getSentimentDetail: id => api.get(`/analysis/sentiment/detail/${id}`),
  runDemand: data => api.post('/analysis/demand/run', data, { timeout: 120000 }),
  getDemandResults: params => api.get('/analysis/demand/results', { params }),
  getComparison: params => api.get('/analysis/comparison', { params }),
}

export const crawlApi = {
  getTasks: params => api.get('/crawl/tasks', { params }),
  createTask: data => api.post('/crawl/tasks', data),
  getTask: id => api.get(`/crawl/tasks/${id}`),
  startTask: id => api.post(`/crawl/tasks/${id}/start`),
  deleteTask: id => api.delete(`/crawl/tasks/${id}`),
}

export const dashboardApi = {
  getStats: () => api.get('/dashboard/stats'),
  getRecentReviews: () => api.get('/dashboard/recent-reviews'),
  getTopProducts: () => api.get('/dashboard/top-products'),
  getCategoryStats: () => api.get('/dashboard/category-stats'),
  getSentimentTrend: () => api.get('/dashboard/sentiment-trend'),
}

export const visualizationApi = {
  getSentimentPie: id => api.get(`/visualization/sentiment-pie/${id}`),
  getSentimentBar: () => api.get('/visualization/sentiment-bar'),
  getSentimentTrend: () => api.get('/visualization/sentiment-trend-chart'),
  getWordcloud: id => api.get(`/visualization/wordcloud/${id}`),
  getCategoryPie: () => api.get('/visualization/category-pie'),
}

export const uploadApi = {
  uploadImage: file => {
    const formData = new FormData()
    formData.append('file', file)
    return api.post('/upload/image', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },
}

export default api
