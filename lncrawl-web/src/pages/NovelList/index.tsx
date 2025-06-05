import { API_BASE_URL } from '@/config';
import type { Novel, PaginatiedResponse } from '@/types';
import {
  Card,
  Col,
  Pagination,
  Row,
  Spin,
  Tag,
  Typography,
  message,
} from 'antd';
import axios from 'axios';
import { useEffect, useState } from 'react';

const { Title, Paragraph } = Typography;

const NovelListPage = () => {
  const [novels, setNovels] = useState<Novel[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);

  const fetchNovels = async (pageNum = 1) => {
    setLoading(true);
    try {
      const limit = 8;
      const offset = (pageNum - 1) * limit;
      const { data } = await axios.get<PaginatiedResponse<Novel>>(
        '/api/novels',
        {
          params: { offset, limit, with_orphans: true },
        }
      );
      setNovels(data.items);
      setTotal(data.total);
    } catch (error) {
      message.error('Failed to fetch novels');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchNovels(page);
  }, [page]);

  if (loading) return <Spin style={{ display: 'block', marginTop: 100 }} />;

  return (
    <div style={{ padding: '20px 40px' }}>
      <Title level={2}>📚 Available Novels</Title>
      <Row gutter={[24, 24]}>
        {novels.map((novel) => (
          <Col key={novel.id} xs={24} lg={12} xl={8} xxl={6}>
            <Card
              hoverable
              cover={
                novel.cover ? (
                  <img
                    alt="cover"
                    src={`${API_BASE_URL}/api/novel/${novel.id}/cover`}
                    style={{ height: 240, objectFit: 'cover' }}
                  />
                ) : null
              }
              style={{ borderRadius: 12 }}
            >
              <Card.Meta
                title={novel.title || 'Untitled'}
                description={
                  <Paragraph ellipsis={{ rows: 3 }}>
                    {novel.synopsis || 'No synopsis available'}
                  </Paragraph>
                }
              />
              <div style={{ marginTop: 10 }}>
                <Typography.Text>
                  Authors: <b>{novel.authors}</b>
                </Typography.Text>
                {novel.tags?.slice(0, 2).map((tag) => (
                  <Tag key={tag} style={{ textTransform: 'capitalize' }}>
                    <Typography.Text ellipsis>
                      {tag.toLowerCase()}
                    </Typography.Text>
                  </Tag>
                ))}
              </div>
            </Card>
          </Col>
        ))}
      </Row>

      {novels.length > 0 && (
        <Pagination
          current={page}
          total={total}
          pageSize={12}
          onChange={(p) => setPage(p)}
          style={{ marginTop: 30, textAlign: 'center' }}
          showSizeChanger={false}
        />
      )}
    </div>
  );
};

export default NovelListPage;
