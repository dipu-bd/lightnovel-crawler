import { type Artifact, type Novel, type Volume } from '@/types';
import { stringifyError } from '@/utils/errors';
import { Button, Flex, Grid, message, Result, Space, Spin } from 'antd';
import axios from 'axios';
import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { ArtifactListCard } from '../../components/ArtifactList/ArtifactListCard';
import { NovelDetailsCard } from './NovelDetailsCard';
import { NovelTableOfContentsCard } from './NovelChapterListCard';
import { getChapterReadStatus } from '../NovelReaderPage/readStatus';

export const NovelDetailsPage: React.FC<any> = () => {
  const { id } = useParams<{ id: string }>();

  const { lg } = Grid.useBreakpoint();
  const [messageApi, contextHolder] = message.useMessage();

  const [refreshId, setRefreshId] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>();

  const [novel, setNovel] = useState<Novel>();
  const [artifacts, setArtifacts] = useState<Artifact[]>([]);
  const [volumes, setVolumes] = useState<Volume[]>([]);

  const fetchNovel = async (id: string) => {
    setError(undefined);
    try {
      const { data } = await axios.get<Novel>(`/api/novel/${id}`);
      setNovel(data);
    } catch (err: any) {
      setError(stringifyError(err));
    } finally {
      setLoading(false);
    }
  };

  const fetchArtifacts = async (id: string) => {
    try {
      const { data } = await axios.get<Artifact[]>(
        `/api/novel/${id}/artifacts`
      );
      setArtifacts(data);
    } catch (err) {
      messageApi.open({
        type: 'error',
        content: stringifyError(err, 'Failed to fetch artifacts'),
      });
    }
  };

  const fetchToc = async (id: string) => {
    try {
      // fetch volume and chapter list
      const { data } = await axios.get<Volume[]>(`/api/novel/${id}/toc`);
      setVolumes([...data]);

      // update read status
      await Promise.all(
        data.flatMap(async (volume) => {
          const reads = await Promise.all(
            volume.chapters.map(async (chapter) => {
              chapter.isRead = await getChapterReadStatus(id, chapter.id);
              return chapter.isRead ? 1 : 0;
            })
          );
          volume.isRead = reads.indexOf(0) < 0;
        })
      );
      setVolumes([...data]);
    } catch (err) {
      messageApi.open({
        type: 'error',
        content: stringifyError(err, 'Failed to fetch TOC'),
      });
    }
  };

  useEffect(() => {
    if (id) {
      fetchNovel(id);
      fetchArtifacts(id);
      fetchToc(id);
    }
  }, [id, refreshId]);

  if (loading) {
    return (
      <Flex align="center" justify="center" style={{ height: '100%' }}>
        <Spin size="large" style={{ marginTop: 100 }} />
      </Flex>
    );
  }

  if (error || !novel || !id) {
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

  return (
    <Space direction="vertical" size={lg ? 'large' : 'small'}>
      {contextHolder}
      <NovelDetailsCard novel={novel} />
      <ArtifactListCard artifacts={artifacts} />
      <NovelTableOfContentsCard toc={volumes} />
    </Space>
  );
};
