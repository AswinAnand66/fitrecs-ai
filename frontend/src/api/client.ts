import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests if available
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle 401 responses
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export interface LoginData {
  email: string;
  password: string;
}

export interface SignupData {
  email: string;
  username: string;
  password: string;
}

export interface User {
  id: number;
  email: string;
  username: string;
  role: 'user' | 'admin';
}

export interface Item {
  id: number;
  title: string;
  type: 'article' | 'workout' | 'video';
  description: string;
  tags: string[];
  duration: number;
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  media_url?: string;
  similarity_score?: number;
}

export interface InteractionData {
  item_id: number;
  interaction_type: 'view' | 'like' | 'complete';
}

export interface AIRecommendationResponse {
  items: Item[];
  explanation: string;
}

export interface ExplanationResponse {
  explanation: string;
}

const api = {
  auth: {
    login: (data: LoginData) =>
      apiClient.post<{ access_token: string }>('/auth/token', data),
    signup: (data: SignupData) =>
      apiClient.post<User>('/auth/signup', data),
    me: () => apiClient.get<User>('/auth/me'),
  },
  
  items: {
    list: () => apiClient.get<Item[]>('/items'),
    get: (id: number) => apiClient.get<Item>(`/items/${id}`),
    search: (query: string) => apiClient.get<Item[]>(`/items/search?q=${query}`),
    upload: (file: File) => {
      const formData = new FormData();
      formData.append('file', file);
      return apiClient.post('/items/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
    },
    rebuildIndex: () => apiClient.post('/items/rebuild-index'),
  },
  
  recommendations: {
    content: (itemId: number, topn: number = 10) =>
      apiClient.get<Item[]>(`/recommend/content/${itemId}?topn=${topn}`),
    collaborative: (userId: number, topn: number = 10) =>
      apiClient.get<Item[]>(`/recommend/collaborative/${userId}?topn=${topn}`),
    hybrid: (userId: number, itemId?: number, topn: number = 10, alpha: number = 0.5) => {
      let url = `/recommend/hybrid/${userId}?topn=${topn}&alpha=${alpha}`;
      if (itemId) url += `&item_id=${itemId}`;
      return apiClient.get<Item[]>(url);
    },
  },
  
  ai: {
    contextualRecommendations: (limit: number = 5) =>
      apiClient.get<AIRecommendationResponse>(`/ai/recommendations/contextual?limit=${limit}`),
    explainRecommendation: (itemId: number) =>
      apiClient.get<ExplanationResponse>(`/ai/explain/${itemId}`),
    chat: (message: string, context?: Array<{ text: string; type: 'user' | 'assistant' }>) =>
      apiClient.post<{ response: string }>('/ai/chat', { message, context }),
  },
  
  interactions: {
    create: (data: InteractionData) =>
      apiClient.post('/interactions', data),
    list: () => apiClient.get('/interactions/me'),
  },
};

export default api;