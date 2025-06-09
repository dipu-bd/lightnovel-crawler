import '@fontsource/roboto-slab/400.css';
import './reader.scss';

import { type ChapterBody } from '@/types';
import { stringifyError } from '@/utils/errors';
import { LeftOutlined, MenuOutlined, RightOutlined } from '@ant-design/icons';
import { Button, Card, Divider, Flex, Grid, Result, Spin } from 'antd';
import axios from 'axios';
import { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';

export const NovelReaderPage: React.FC<any> = () => {
  const { sm } = Grid.useBreakpoint();
  const { id, hash } = useParams<{ id: string; hash: string }>();

  const [refreshId, setRefreshId] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>();
  const [chapter, setChapter] = useState<ChapterBody>();

  const fetchChapter = async (id: string, hash: string) => {
    setError(undefined);
    try {
      const { data } = await axios.get<ChapterBody>(
        `/api/novel/${id}/chapter/${hash}`
      );
      setChapter(data);
    } catch (err: any) {
      setError(stringifyError(err));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (id && hash) {
      fetchChapter(id, hash);
    }
  }, [id, hash, refreshId]);

  if (loading) {
    return (
      <Flex align="center" justify="center" style={{ height: '100%' }}>
        <Spin tip="Loading job..." size="large" style={{ marginTop: 100 }} />
      </Flex>
    );
  }

  if (error || !chapter) {
    return (
      <Flex align="center" justify="center" style={{ height: '100%' }}>
        <Result
          status="error"
          title="Failed to load novel details"
          subTitle={error}
          extra={[
            <Button onClick={() => setRefreshId((v) => v + 1)}>Retry</Button>,
          ]}
        />
      </Flex>
    );
  }

  const NavigationButtons = () => {
    const navigate = useNavigate();

    // TODO: get it from api
    const prev = false;
    const next = false;

    return (
      <Flex align="center" justify="space-between">
        <Button disabled={!prev}>
          <LeftOutlined />
          Previous
        </Button>
        <Button>
          <MenuOutlined onClick={() => navigate(`/novel/${id}`)} />
        </Button>
        <Button disabled={!next}>
          Next <RightOutlined />
        </Button>
      </Flex>
    );
  };

  return (
    <Card
      size={sm ? 'default' : 'small'}
      style={{ maxWidth: 1024, margin: '0 auto' }}
    >
      <Flex vertical>
        <NavigationButtons />
        <Divider />
        <div
          className="novel-content-reader"
          dangerouslySetInnerHTML={{ __html: chapter.body }}
        />
        <Divider />
        <NavigationButtons />
      </Flex>
    </Card>
  );
};
