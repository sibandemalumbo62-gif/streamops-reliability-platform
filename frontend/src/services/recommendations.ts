import api from './api';

export interface Recommendation {
  content_id: string;
  title: string;
  score: number;
  reason: string;
}

export interface WatchHistory {
  content_id: string;
  watched_at: string;
  completion_percentage: number;
}

export interface UserPreferences {
  user_id: string;
  preferred_genres: string[];
  language: string;
  quality_preference: string;
}

export const recommendationService = {
  async getRecommendations(userId: string): Promise<Recommendation[]> {
    const response = await api.get(`/api/v1/recommendations/${userId}`);
    return response.data;
  },

  async addWatchHistory(userId: string, contentId: string, completionPercentage: number): Promise<void> {
    await api.post('/api/v1/recommendations/watch-history', {
      user_id: userId,
      content_id: contentId,
      completion_percentage: completionPercentage,
    });
  },

  async getWatchHistory(userId: string): Promise<WatchHistory[]> {
    const response = await api.get(`/api/v1/recommendations/${userId}/watch-history`);
    return response.data;
  },

  async getPreferences(userId: string): Promise<UserPreferences> {
    const response = await api.get(`/api/v1/preferences/${userId}`);
    return response.data;
  },

  async createPreferences(data: UserPreferences): Promise<UserPreferences> {
    const response = await api.post('/api/v1/preferences/', data);
    return response.data;
  },

  async updatePreferences(userId: string, data: Partial<UserPreferences>): Promise<UserPreferences> {
    const response = await api.patch(`/api/v1/preferences/${userId}`, data);
    return response.data;
  },
};
