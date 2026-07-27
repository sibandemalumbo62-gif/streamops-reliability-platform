import api from './api';

export interface PlaybackSession {
  id: string;
  user_id: string;
  content_id: string;
  started_at: string;
  position: number;
  status: string;
  device_type: string;
}

export interface CreateSessionData {
  user_id: string;
  content_id: string;
  device_type: string;
}

export const playbackService = {
  async startSession(data: CreateSessionData): Promise<PlaybackSession> {
    const response = await api.post('/api/v1/playback/start', data);
    return response.data;
  },

  async getStreamUrl(sessionId: string): Promise<{ stream_url: string }> {
    const response = await api.post(`/api/v1/playback/${sessionId}/stream-url`);
    return response.data;
  },

  async pauseSession(sessionId: string): Promise<void> {
    await api.post(`/api/v1/playback/${sessionId}/pause`);
  },

  async resumeSession(sessionId: string): Promise<void> {
    await api.post(`/api/v1/playback/${sessionId}/resume`);
  },

  async stopSession(sessionId: string): Promise<void> {
    await api.post(`/api/v1/playback/${sessionId}/stop`);
  },

  async getSession(sessionId: string): Promise<PlaybackSession> {
    const response = await api.get(`/api/v1/sessions/${sessionId}`);
    return response.data;
  },

  async getActiveSessions(userId: string): Promise<PlaybackSession[]> {
    const response = await api.get(`/api/v1/sessions/user/${userId}/active`);
    return response.data;
  },
};
