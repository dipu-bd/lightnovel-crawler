import { API_BASE_URL } from '@/config';
import type { Novel } from '@/types';
import { Avatar, Card, Flex, Image, Tooltip, Typography } from 'antd';
import { useMemo } from 'react';
import { useNavigate } from 'react-router-dom';

export const NovelListItemCard: React.FC<{ novel: Novel }> = ({ novel }) => {
  const navigate = useNavigate();

  const novelUrl = useMemo(() => new URL(novel.url), [novel.url]);

  const faviconLink = useMemo(
    () => novelUrl.origin + '/favicon.ico',
    [novelUrl]
  );

  const domainName = useMemo(
    () => novelUrl.hostname.replace('www.', ''),
    [novelUrl]
  );

  return (
    <Tooltip
      title={
        <Flex wrap gap="5px">
          <Typography.Text strong>{novel.title}</Typography.Text>
          <Typography.Text type="secondary">({domainName})</Typography.Text>
        </Flex>
      }
    >
      <Card
        hoverable
        style={{
          height: '100%',
          overflow: 'clip',
          position: 'relative',
          background: '#eee',
          userSelect: 'none',
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
        <Avatar
          size="small"
          src={faviconLink}
          style={{
            position: 'absolute',
            top: 3,
            left: 5,
            backdropFilter: 'blur(10px)',
          }}
        />
        {novel.title && novel.title !== '...' && (
          <Typography.Paragraph
            strong
            ellipsis={{ rows: 2 }}
            style={{
              position: 'absolute',
              bottom: 0,
              left: 0,
              right: 0,
              margin: 0,
              padding: '3px 5px',
              textAlign: 'center',
              fontSize: '12px',
              backdropFilter: 'blur(5px)',
              background: 'rgba(0, 0, 0, 0.5)',
            }}
          >
            {novel.title}
          </Typography.Paragraph>
        )}
      </Card>
    </Tooltip>
  );
};
