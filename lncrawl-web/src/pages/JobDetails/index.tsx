import {
  JobStatus,
  type Artifact,
  type Job,
  type JobDetails,
  type Novel,
  type User,
} from '@/types';
import { stringifyError } from '@/utils/errors';
import { Button, Flex, Grid, Result, Space, Spin } from 'antd';
import axios from 'axios';
import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { ArtifactListCard } from '../../components/ArtifactList/ArtifactListCard';
import { NovelDetailsCard } from '../NovelDetails/NovelDetailsCard';
import { UserDetailsCard } from '../UserDetails/UserDetailsCard';
import { JobDetailsCard } from './JobDetailsCard';

export const JobDetailsPage: React.FC<any> = () => {
  const { lg } = Grid.useBreakpoint();
  const { id } = useParams<{ id: string }>();

  const [refreshId, setRefreshId] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>();

  const [job, setJob] = useState<Job>();
  const [novel, setNovel] = useState<Novel>();
  const [user, setUser] = useState<User>();
  const [artifacts, setArtifacts] = useState<Artifact[]>([]);

  const fetchJob = async (id: string) => {
    setError(undefined);
    try {
      const { data } = await axios.get<JobDetails>(`/api/job/${id}`);
      setJob(data.job);
      setUser(data.user);
      setNovel(data.novel);
      setArtifacts(data.artifacts);
    } catch (err: any) {
      setError(stringifyError(err));
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
      }, 2000);
      return () => {
        clearInterval(iid);
      };
    }
  }, [job]);

  if (loading) {
    return (
      <Flex align="center" justify="center" style={{ height: '100%' }}>
        <Spin tip="Loading job..." size="large" style={{ marginTop: 100 }} />
      </Flex>
    );
  }

  if (!job || !user) {
    return (
      <Flex align="center" justify="center" style={{ height: '100%' }}>
        <Result
          status="error"
          title="Failed to load job data"
          subTitle={error}
          extra={[
            <Button
              onClick={() => {
                setLoading(true);
                setRefreshId((v) => v + 1);
              }}
            >
              Retry
            </Button>,
          ]}
        />
      </Flex>
    );
  }

  return (
    <Space direction="vertical" size={lg ? 'large' : 'small'}>
      <JobDetailsCard job={job} />
      <UserDetailsCard user={user} />
      <NovelDetailsCard novel={novel} />
      <ArtifactListCard artifacts={artifacts} />
    </Space>
  );
};
