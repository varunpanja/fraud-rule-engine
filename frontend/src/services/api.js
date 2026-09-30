import axios from 'axios';

const API_BASE = '/api';

const client = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const api = {
  // Dashboard Metrics
  getDashboardStats: async () => {
    const res = await client.get('/dashboard/stats');
    return res.data;
  },

  // Fraud Flags
  getFraudFlags: async (params = {}) => {
    const res = await client.get('/fraud/flags', { params });
    return res.data;
  },

  getFraudFlag: async (id) => {
    const res = await client.get(`/fraud/flags/${id}`);
    return res.data;
  },

  reviewFraudFlag: async (id, reviewer_notes = '') => {
    const res = await client.put(`/fraud/flags/${id}/review`, { reviewer_notes });
    return res.data;
  },

  clearFraudFlag: async (id, reviewer_notes = '') => {
    const res = await client.put(`/fraud/flags/${id}/clear`, { reviewer_notes });
    return res.data;
  },

  // Transactions
  getTransactions: async (params = {}) => {
    const res = await client.get('/transactions', { params });
    return res.data;
  },

  getTransaction: async (id) => {
    const res = await client.get(`/transactions/${id}`);
    return res.data;
  },

  createTransaction: async (payload) => {
    const res = await client.post('/transactions', payload);
    return res.data;
  },

  // Demo utilities
  seedDemo: async () => {
    const res = await client.post('/demo/seed');
    return res.data;
  },

  resetDemo: async () => {
    const res = await client.post('/demo/reset');
    return res.data;
  },
};

export default api;
