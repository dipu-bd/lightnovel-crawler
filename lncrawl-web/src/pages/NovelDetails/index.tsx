import { type Artifact, type Novel } from '@/types';
import { Button, Flex, Result, Space, Spin } from 'antd';
import axios from 'axios';
import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { ArtifactListView } from '../ArtifactDetails/ArtifactListView';
import { NovelDetailsView } from '../NovelDetails/NovelDetailsView';

export default function JobDetailsPage() {
  const { id } = useParams<{ id: string }>();

  const [refreshId, setRefreshId] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>();

  const [novel, setNovel] = useState<Novel>();
  const [artifacts, setArtifacts] = useState<Artifact[]>([]);

  const fetchNovel = async (id: string) => {
    try {
      const { data } = await axios.get<Novel>(`/api/novel/${id}`);
      setNovel(data);
    } catch (err: any) {
      setError(err.message || String(err));
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
    } catch {}
  };

  useEffect(() => {
    if (id) {
      fetchNovel(id);
      fetchArtifacts(id);
    }
  }, [id, refreshId]);

  if (loading) {
    return (
      <Flex align="center" justify="center" style={{ height: '100%' }}>
        <Spin tip="Loading job..." size="large" style={{ marginTop: 100 }} />
      </Flex>
    );
  }

  if (error || !novel) {
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
    <Space
      size="large"
      direction="vertical"
      style={{ padding: 15, marginBottom: '20px' }}
    >
      <NovelDetailsView novel={novel} />
      <ArtifactListView artifacts={artifacts} />
    </Space>
  );
}
