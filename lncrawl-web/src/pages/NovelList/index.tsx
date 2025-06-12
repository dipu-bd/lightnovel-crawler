import {
  Button,
  Col,
  Divider,
  Empty,
  Flex,
  Pagination,
  Result,
  Row,
  Spin,
  Typography,
} from 'antd';
import { useNovelList } from './hooks';
import { NovelListItemCard } from './NovelListItemCard';
import { RequestNovelCard } from './RequestNovelCard';

const { Title } = Typography;

export const NovelListPage: React.FC<any> = () => {
  const {
    currentPage,
    perPage,
    error,
    loading,
    total,
    novels,
    refresh,
    changePage,
  } = useNovelList();

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
          extra={[<Button onClick={refresh}>Retry</Button>]}
        />
      </Flex>
    );
  }

  return (
    <>
      <Title level={2}>📘 Request Novel</Title>

      <RequestNovelCard />

      <Divider />

      <Title level={2}>📚 Available Novels</Title>

      <Row gutter={[16, 16]}>
        {novels.map((novel) => (
          <Col key={novel.id} xs={12} sm={8} lg={6} xl={4}>
            <NovelListItemCard novel={novel} />
          </Col>
        ))}
      </Row>

      {!novels.length && (
        <Flex align="center" justify="center" style={{ height: '100%' }}>
          <Empty image={Empty.PRESENTED_IMAGE_SIMPLE} description="No novels" />
        </Flex>
      )}

      {(novels.length > 0 || currentPage > 1) && total / perPage > 1 && (
        <Pagination
          current={currentPage}
          total={total}
          pageSize={perPage}
          showSizeChanger={false}
          onChange={changePage}
          style={{ textAlign: 'center', marginTop: 32 }}
        />
      )}
    </>
  );
};
