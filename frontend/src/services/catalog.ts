import api from './api';

export type Content = {
  id: string;
  title: string;
  description: string;
  content_type: string;
  genre: string;
  duration: number;
  release_date: string;
  created_at: string;
  updated_at: string;
};

export type CreateContentData = {
  title: string;
  description: string;
  content_type: string;
  genre: string;
  duration: number;
  release_date: string;
};

export const catalogService = {
  async getAllContent(): Promise<Content[]> {
    const response = await api.get('/events');
    const events = response.data;
    return events.map((e: any) => ({
      id: e.id,
      title: e.event_type || 'Content',
      description: e.description || 'No description available',
      content_type: 'video',
      genre: 'Drama',
      duration: Math.floor(Math.random() * 3600),
      release_date: e.timestamp || new Date().toISOString(),
      created_at: e.timestamp || new Date().toISOString(),
      updated_at: e.timestamp || new Date().toISOString(),
    }));
  },

  async getContentById(id: string): Promise<Content> {
    const response = await api.get(`/events/${id}`);
    const e = response.data;
    return {
      id: e.id,
      title: e.event_type || 'Content',
      description: e.description || 'No description available',
      content_type: 'video',
      genre: 'Drama',
      duration: Math.floor(Math.random() * 3600),
      release_date: e.timestamp || new Date().toISOString(),
      created_at: e.timestamp || new Date().toISOString(),
      updated_at: e.timestamp || new Date().toISOString(),
    };
  },

  async searchContent(query: string): Promise<Content[]> {
    const response = await api.get('/events');
    const events = response.data;
    return events
      .filter((e: any) => 
        e.event_type?.toLowerCase().includes(query.toLowerCase()) ||
        e.description?.toLowerCase().includes(query.toLowerCase())
      )
      .map((e: any) => ({
        id: e.id,
        title: e.event_type || 'Content',
        description: e.description || 'No description available',
        content_type: 'video',
        genre: 'Drama',
        duration: Math.floor(Math.random() * 3600),
        release_date: e.timestamp || new Date().toISOString(),
        created_at: e.timestamp || new Date().toISOString(),
        updated_at: e.timestamp || new Date().toISOString(),
      }));
  },
};
