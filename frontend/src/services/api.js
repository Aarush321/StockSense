import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5001/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  }
})

export const analyzeStock = async (symbol) => {
  try {
    const response = await api.post('/analyze', { symbol })
    return response.data
  } catch (error) {
    throw new Error(error.response?.data?.error || 'Failed to analyze stock')
  }
}

export const getStarredStocks = async () => {
  try {
    const response = await api.get('/starred')
    return response.data
  } catch (error) {
    throw new Error(error.response?.data?.error || 'Failed to fetch starred stocks')
  }
}

export const starStock = async (symbol) => {
  try {
    const response = await api.post('/star', { symbol })
    return response.data
  } catch (error) {
    throw new Error(error.response?.data?.error || 'Failed to star stock')
  }
}

export const unstarStock = async (symbol) => {
  try {
    const response = await api.delete(`/star/${symbol}`)
    return response.data
  } catch (error) {
    throw new Error(error.response?.data?.error || 'Failed to unstar stock')
  }
}

export const refreshStock = async (symbol) => {
  try {
    const response = await api.get(`/refresh/${symbol}`)
    return response.data
  } catch (error) {
    throw new Error(error.response?.data?.error || 'Failed to refresh stock data')
  }
}

