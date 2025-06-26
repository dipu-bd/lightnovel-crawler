import '@fontsource/arbutus-slab/400.css';
import '@fontsource/roboto-slab/400.css';
import './reader.scss';

import { type ChapterBody } from '@/types';
import { stringifyError } from '@/utils/errors';
import { LeftOutlined, MenuOutlined, RightOutlined } from '@ant-design/icons';
import { Button, Divider, Flex, Result, Spin } from 'antd';
import axios from 'axios';
import { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { setChapterReadStatus } from './readStatus';

export const NovelReaderPage: React.FC<any> = () => {
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
      setChapterReadStatus(id, data.id);
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
        <Spin size="large" style={{ marginTop: 100 }} />
      </Flex>
    );
  }

  if (error || !chapter || !id) {
    return (
      <Flex align="center" justify="center" style={{ height: '100%' }}>
        <Result
          status="error"
          title="Failed to load chapter content"
          subTitle={error}
          extra={[
            <Button onClick={() => setRefreshId((v) => v + 1)}>Retry</Button>,
          ]}
        />
      </Flex>
    );
  }

  return (
    <>
      <Flex vertical>
        <NavigationButtons novelId={id} chapter={chapter} />
        <Divider />
        <div
          className="novel-content-reader"
          dangerouslySetInnerHTML={{ __html: chapter.body }}
        />
        <Divider />
        <NavigationButtons novelId={id} chapter={chapter} />
      </Flex>
    </>
  );
};

export const NavigationButtons: React.FC<{
  novelId: string;
  chapter: ChapterBody;
}> = ({ novelId, chapter }) => {
  const navigate = useNavigate();

  const prev = chapter?.prev?.hash;
  const next = chapter?.next?.hash;

  return (
    <Flex align="center" justify="space-between">
      <Button
        disabled={!prev}
        onClick={() => navigate(`/novel/${novelId}/chapter/${prev}`)}
      >
        <LeftOutlined />
        Previous
      </Button>
      <Button onClick={() => navigate(`/novel/${novelId}`)}>
        <MenuOutlined />
      </Button>
      <Button
        disabled={!next}
        onClick={() => navigate(`/novel/${novelId}/chapter/${next}`)}
      >
        Next <RightOutlined />
      </Button>
    </Flex>
  );
};
