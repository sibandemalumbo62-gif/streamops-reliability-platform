import { useState, useEffect } from 'react';
import { catalogService, type Content } from '../services/catalog';
import { Search, Play } from 'lucide-react';

export default function Catalog() {
  const [content, setContent] = useState<Content[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    loadContent();
  }, []);

  const loadContent = async () => {
    try {
      const data = await catalogService.getAllContent();
      setContent(data);
      setError('');
    } catch (error: any) {
      console.error('Failed to load content:', error);
      setError('Failed to load content. Backend may not be running.');
      // Set mock data for demo
      setContent([
        {
          id: '1',
          title: 'Sample Video 1',
          description: 'This is a sample video description for demo purposes.',
          content_type: 'video',
          genre: 'Drama',
          duration: 3600,
          release_date: new Date().toISOString(),
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        },
        {
          id: '2',
          title: 'Sample Video 2',
          description: 'Another sample video for demonstration.',
          content_type: 'video',
          genre: 'Comedy',
          duration: 2400,
          release_date: new Date().toISOString(),
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async () => {
    if (searchQuery) {
      try {
        const data = await catalogService.searchContent(searchQuery);
        setContent(data);
        setError('');
      } catch (error: any) {
        console.error('Search failed:', error);
        setError('Search failed. Using local data.');
      }
    } else {
      loadContent();
    }
  };

  if (loading) {
    return <div className="p-8">Loading...</div>;
  }

  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold mb-6">Media Library</h1>
      
      {error && (
        <div className="bg-yellow-100 border border-yellow-400 text-yellow-700 px-4 py-3 rounded mb-6">
          {error}
        </div>
      )}
      
      <div className="flex gap-4 mb-6">
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
          <input
            type="text"
            placeholder="Search content..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
            className="w-full pl-10 pr-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
        <button
          onClick={handleSearch}
          className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600"
        >
          Search
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        {content.map((item) => (
          <div key={item.id} className="bg-white rounded-lg shadow overflow-hidden">
            <div className="aspect-video bg-gray-200 flex items-center justify-center">
              <Play className="text-gray-400" size={48} />
            </div>
            <div className="p-4">
              <h3 className="font-semibold text-lg mb-2">{item.title}</h3>
              <p className="text-gray-600 text-sm mb-3 line-clamp-2">{item.description}</p>
              <div className="flex items-center justify-between text-sm text-gray-500">
                <span>{item.genre}</span>
                <span>{Math.floor(item.duration / 60)}m</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
