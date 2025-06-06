import {
  JobStatus,
  type Artifact,
  type Job,
  type JobDetails,
  type Novel,
  type User,
} from '@/types';
import { Button, Flex, Result, Space, Spin } from 'antd';
import axios from 'axios';
import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { JobDetailsView } from './JobDetailsView';
import { UserDetailsView } from '../UserDetails/UserDetailsView';
import { NovelDetailsView } from '../NovelDetails/NovelDetailsView';
import { ArtifactListView } from '../ArtifactList/ArtifactListView';

export default function JobDetailsPage() {
  const { id } = useParams<{ id: string }>();

  const [refreshId, setRefreshId] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>();

  const [job, setJob] = useState<Job>();
  const [novel, setNovel] = useState<Novel>();
  const [user, setUser] = useState<User>();
  const [artifacts, setArtifacts] = useState<Artifact[]>([]);

  const fetchJob = async (id: string) => {
    try {
      const { data } = await axios.get<JobDetails>(`/api/job/${id}`);
      setJob(data.job);
      setUser(data.user);
      setNovel(data.novel);
      setArtifacts(data.artifacts);
    } catch (err: any) {
      setError(err.message || String(err));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (id) {
      fetchJob(id);
    }
  }, [id, refreshId]);

  useEffect(() => {
    if (job && job.status !== JobStatus.COMPLETED) {
      const iid = setInterval(() => {
        setRefreshId((v) => v + 1);
      }, 1000);
      return () => {
        clearInterval(iid);
      };
    }
  }, [job?.status]);

  if (loading) {
    return (
      <Flex align="center" justify="center" style={{ height: '100%' }}>
        <Spin tip="Loading job..." size="large" style={{ marginTop: 100 }} />
      </Flex>
    );
  }

  if (error || !job || !user) {
    return (
      <Flex align="center" justify="center" style={{ height: '100%' }}>
        <Result
          status="error"
          title="Failed to load job data"
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
      style={{ padding: 15, marginBottom: 20 }}
    >
      <JobDetailsView job={job} />
      <UserDetailsView user={user} />
      <NovelDetailsView novel={novel} />
      <ArtifactListView artifacts={artifacts} />
    </Space>
  );
}
