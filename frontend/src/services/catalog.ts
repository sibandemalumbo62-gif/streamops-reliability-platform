import api from './api';

export interface Content {
  id: string;
  title: string;
  description: string;
  content_type: string;
  genre: string;
  duration: number;
  release_date: string;
  created_at: string;
  updated_at: string;
}

export interface CreateContentData {
  title: string;
  description: string;
  content_type: string;
  genre: string;
  duration: number;
  release_date: string;
}

export const catalogService = {
  async getAllContent(): Promise<Content[]> {
    const response = await api.get('/api/v1/catalog/');
    return response.data;
  },

  async getContentById(id: string): Promise<Content> {
    const response = await api.get(`/api/v1/catalog/${id}`);
    return response.data;
  },

  async createContent(data: CreateContentData): Promise<Content> {
    const response = await api.post('/api/v1/catalog/', data);
    return response.data;
  },

  async updateContent(id: string, data: Partial<Content>): Promise<Content> {
    const response = await api.patch(`/api/v1/catalog/${id}`, data);
    return response.data;
  },

  async deleteContent(id: string): Promise<void> {
    await api.delete(`/api/v1/catalog/${id}`);
  },

  async searchContent(query: string): Promise<Content[]> {
    const response = await api.get(`/api/v1/search/?q=${query}`);
    return response.data;
  },
};
