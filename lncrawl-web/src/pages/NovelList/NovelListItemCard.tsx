import { API_BASE_URL } from '@/config';
import type { Novel } from '@/types';
import { Card, Image } from 'antd';
import { useNavigate } from 'react-router-dom';

export const NovelListItemCard: React.FC<{ novel: Novel }> = ({ novel }) => {
  const navigate = useNavigate();

  return (
    <Card
      hoverable
      style={{
        height: '100%',
        overflow: 'clip',
        position: 'relative',
        background: '#eee',
      }}
      onClick={() => navigate(`/novel/${novel.id}`)}
      styles={{
        body: { padding: 0 },
      }}
    >
      <Image
        alt="cover"
        preview={false}
        src={`${API_BASE_URL}/api/novel/${novel.id}/cover`}
        fallback="/no-image.svg"
        loading="lazy"
        fetchPriority="low"
        style={{
          objectFit: 'cover',
          aspectRatio: 3 / 4,
          minHeight: '100%',
          maxHeight: '50vh',
        }}
      />
      <div
        title={novel.title}
        style={{
          position: 'absolute',
          bottom: 0,
          left: 0,
          right: 0,
          background: '#000000bf',
          margin: 0,
          padding: 5,
          textAlign: 'center',
          fontWeight: 'bold',
        }}
      >
        {novel.title || <i>No Title</i>}
      </div>
    </Card>
  );
};
