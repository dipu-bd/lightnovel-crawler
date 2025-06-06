import type { Novel, PaginatiedResponse } from '@/types';
import {
  Button,
  Col,
  Empty,
  Flex,
  Pagination,
  Result,
  Row,
  Spin,
  Typography,
} from 'antd';
import axios from 'axios';
import { useEffect, useMemo, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { NovelListItemCard } from './NovelListItemCard';

const { Title } = Typography;

const PER_PAGE = 16;

export default function NovelListPage() {
  const [searchParams, setSearchParams] = useSearchParams();

  const [refreshId, setRefreshId] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>();

  const [total, setTotal] = useState(0);
  const [novels, setNovels] = useState<Novel[]>([]);

  const currentPage = useMemo(
    () => parseInt(searchParams.get('page') || '1', 10),
    [searchParams]
  );

  const fetchNovels = async (page: number) => {
    setLoading(true);
    try {
      const offset = (page - 1) * PER_PAGE;
      const { data } = await axios.get<PaginatiedResponse<Novel>>(
        '/api/novels',
        {
          params: { offset, limit: PER_PAGE },
        }
      );
      setTotal(data.total);
      setNovels(data.items);
    } catch (err: any) {
      console.error('Failed to fetch novels', err);
      setError(err?.message || String(err));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchNovels(currentPage);
  }, [currentPage, refreshId]);

  const handlePageChange = (page: number) => {
    setSearchParams({ page: String(page) });
  };

  if (loading) {
    return (
      <Flex align="center" justify="center" style={{ height: '100%' }}>
        <Spin tip="Loading job..." size="large" style={{ marginTop: 100 }} />
      </Flex>
    );
  }

  if (error) {
    return (
      <Flex align="center" justify="center" style={{ height: '100%' }}>
        <Result
          status="error"
          title="Failed to load novel list"
          subTitle={error}
          extra={[
            <Button onClick={() => setRefreshId((v) => v + 1)}>Retry</Button>,
          ]}
        />
      </Flex>
    );
  }

  return (
    <div style={{ padding: '0 15px', height: '100%', marginBottom: '20px' }}>
      <Title level={2}>📚 Available Novels</Title>

      <Row gutter={[24, 24]}>
        {novels.map((novel) => (
          <Col key={novel.id} xs={24} md={12} lg={8} xl={6} xxl={4}>
            <NovelListItemCard novel={novel} />
          </Col>
        ))}
      </Row>

      {!novels.length && (
        <Flex align="center" justify="center" style={{ height: '100%' }}>
          <Empty image={Empty.PRESENTED_IMAGE_SIMPLE} description="No novels" />
        </Flex>
      )}

      {(novels.length > 0 || currentPage > 1) && total / PER_PAGE > 1 && (
        <Pagination
          current={currentPage}
          total={total}
          pageSize={PER_PAGE}
          showSizeChanger={false}
          onChange={handlePageChange}
          style={{ textAlign: 'center', marginTop: 32 }}
        />
      )}
    </div>
  );
}
