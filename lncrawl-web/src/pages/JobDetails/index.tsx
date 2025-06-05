import {
  JobStatus,
  type Artifact,
  type User,
  type Job,
  type JobDetails,
  type Novel,
} from '@/types';
import { Button, Flex, Result, Space, Spin } from 'antd';
import axios from 'axios';
import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { ArtifactListView } from './ArtifactListView';
import { JobDetailsView } from './JobDetailsView';
import { NovelDetailsView } from './NovelDetailsView';
import UserDetailsPage from '../UserDetails';
import { UserDetailsView } from './UserDetailsView';

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
    console.log(
      job?.status,
      JobStatus.COMPLETED,
      job?.status !== JobStatus.COMPLETED
    );
    if (job && job.status !== JobStatus.COMPLETED) {
      const iid = setInterval(() => {
        console.log(refreshId);
        setRefreshId((v) => v + 1);
      }, 100);
      return clearInterval(iid);
    }
  }, [job]);

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
    <Space size="large" direction="vertical" style={{ padding: 24 }}>
      <JobDetailsView job={job} title={novel?.title || job.url} />
      <UserDetailsView user={user} />
      <NovelDetailsView novel={novel} />
      <ArtifactListView artifacts={artifacts} />
    </Space>
  );
}
