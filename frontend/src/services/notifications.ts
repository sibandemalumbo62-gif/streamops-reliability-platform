import api from './api';

export interface Notification {
  id: string;
  user_id: string;
  type: string;
  title: string;
  message: string;
  is_read: boolean;
  created_at: string;
}

export interface CreateNotificationData {
  user_id: string;
  type: string;
  title: string;
  message: string;
  channel: string;
}

export const notificationService = {
  async getUserNotifications(userId: string): Promise<Notification[]> {
    const response = await api.get(`/api/v1/notifications/user/${userId}`);
    return response.data;
  },

  async getNotification(notificationId: string): Promise<Notification> {
    const response = await api.get(`/api/v1/notifications/${notificationId}`);
    return response.data;
  },

  async createNotification(data: CreateNotificationData): Promise<Notification> {
    const response = await api.post('/api/v1/notifications/', data);
    return response.data;
  },

  async markAsRead(notificationId: string): Promise<void> {
    await api.post(`/api/v1/notifications/${notificationId}/read`);
  },

  async markAllAsRead(userId: string): Promise<void> {
    await api.post(`/api/v1/notifications/user/${userId}/read-all`);
  },
};
