import { API_BASE_URL } from '@/config';
import { type Novel } from '@/types';
import { formatDate } from '@/utils/time';
import { ExportOutlined } from '@ant-design/icons';
import {
  Card,
  Descriptions,
  Divider,
  Empty,
  Flex,
  Grid,
  Image,
  Tag,
  Typography,
} from 'antd';
import { useState } from 'react';

const { Title, Link, Paragraph } = Typography;

export const NovelDetailsCard: React.FC<{ novel?: Novel }> = ({ novel }) => {
  const { lg } = Grid.useBreakpoint();
  const [hasMore, setHasMore] = useState<boolean>(false);
  const [showMore, setShowMore] = useState<boolean>(false);

  if (!novel?.title) {
    return (
      <Card variant="outlined" style={{ margin: 'auto', maxWidth: 1000 }}>
        <Empty
          image={Empty.PRESENTED_IMAGE_SIMPLE}
          description="Novel details is not available"
        />
      </Card>
    );
  }

  return (
    <Card variant="outlined" style={{ margin: 'auto', maxWidth: 1000 }}>
      <Title
        level={3}
        style={{ color: 'inherit', margin: 0, marginBottom: 10 }}
      >
        {
          <Link
            href={novel.url}
            target="_blank"
            rel="noreferrer noopener"
            style={{ fontSize: 'inherit' }}
          >
            {novel.title} &nbsp; <ExportOutlined />
          </Link>
        }
      </Title>
      <Flex gap="20px" vertical={!lg}>
        <Flex vertical align="center" justify="center" gap="5px">
          <Image
            alt="Novel Cover"
            src={`${API_BASE_URL}/api/novel/${novel.id}/cover`}
            style={{
              display: 'block',
              objectFit: 'cover',
              borderRadius: 8,
              width: 'auto',
              height: '300px',
            }}
          />
          {novel.tags && novel.tags.length > 0 && (
            <Flex wrap gap="5px" justify={lg ? undefined : 'center'}>
              <Divider size="small" />
              {novel.tags.map((tag) => (
                <Tag
                  key={tag}
                  style={{ textTransform: 'capitalize', margin: 0 }}
                >
                  {tag.toLowerCase()}
                </Tag>
              ))}
            </Flex>
          )}
        </Flex>
        <Flex vertical flex="auto" gap="5px">
          <Descriptions
            size="small"
            layout="horizontal"
            column={lg ? 2 : 1}
            bordered
            items={[
              {
                label: 'Authors',
                span: 2,
                children: novel.authors,
              },
              {
                label: 'Volumes',
                children: novel.volume_count,
              },
              {
                label: 'Chapters',
                children: novel.chapter_count,
              },
              {
                label: 'Created',
                children: formatDate(novel.created_at),
              },
              {
                label: 'Last Updated',
                children: formatDate(novel.updated_at),
              },
            ]}
          />
          <Paragraph
            type="secondary"
            style={{
              textAlign: 'justify',
              overflow: 'hidden',
              maxHeight: showMore ? undefined : '280px',
            }}
            ref={(el) => {
              if (!el) return;
              setHasMore(Math.abs(el.scrollHeight - el.clientHeight) > 10);
            }}
          >
            {novel.synopsis ? (
              <span dangerouslySetInnerHTML={{ __html: novel.synopsis }} />
            ) : (
              'No synopsis available'
            )}
          </Paragraph>
          {(hasMore || showMore) && (
            <Link
              italic
              onClick={() => setShowMore((v) => !v)}
              style={{ textAlign: showMore ? 'left' : 'right' }}
            >
              {showMore ? '< See less' : 'See more >'}
            </Link>
          )}
        </Flex>
      </Flex>
    </Card>
  );
};
