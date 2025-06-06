import { API_BASE_URL } from '@/config';
import type { Novel } from '@/types';
import { Card, Image, Tag, Typography } from 'antd';
import { useNavigate } from 'react-router-dom';

const { Paragraph } = Typography;

export const NovelListItemCard: React.FC<{ novel: Novel }> = ({ novel }) => {
  const navigate = useNavigate();

  return (
    <Card
      hoverable
      style={{ height: '100%', overflow: 'clip' }}
      onClick={() => navigate(`/novel/${novel.id}`)}
      cover={
        <Image
          alt="cover"
          preview={false}
          src={`${API_BASE_URL}/api/novel/${novel.id}/cover`}
          style={{
            objectFit: 'cover',
            aspectRatio: 3 / 4,
            maxHeight: '50vh',
          }}
        />
      }
    >
      <Card.Meta
        title={novel.title || 'Untitled'}
        description={
          novel.synopsis ? (
            <Paragraph ellipsis={{ rows: 3 }}>
              <span dangerouslySetInnerHTML={{ __html: novel.synopsis }} />
            </Paragraph>
          ) : (
            'No synopsis available'
          )
        }
      />
      <Typography.Text>
        Author: <b>{novel.authors}</b>
      </Typography.Text>
      <div style={{ marginTop: 10 }}>
        {(novel.tags || [])?.slice(0, 2).map((tag) => (
          <Tag key={tag} style={{ textTransform: 'capitalize' }}>
            <Typography.Text ellipsis>{tag.toLowerCase()}</Typography.Text>
          </Tag>
        ))}
      </div>
    </Card>
  );
};
