import {
  JobPriorityTag,
  JobStatusTag,
  RunStateTag,
} from '@/components/Tags/jobs';
import { JobStatus, RunState, type Job } from '@/types';
import { formatDate, formatDuration } from '@/utils/time';
import {
  ClockCircleFilled,
  ClockCircleOutlined,
  HourglassFilled,
} from '@ant-design/icons';
import { Alert, Card, Flex, Grid, Space, Tag, Typography } from 'antd';
import { JobActionButtons } from '../JobList/JobActionButtons';
import { JobProgressLine } from '../JobList/JobProgessBar';

const { Title, Text } = Typography;

export const JobDetailsCard: React.FC<{ job: Job }> = ({ job }) => {
  const { lg } = Grid.useBreakpoint();

  return (
    <Card variant="outlined">
      <Title
        level={lg ? 2 : 3}
        style={{
          margin: 0,
          marginBottom: 8,
          fontFamily: "'Roboto Slab', serif",
        }}
      >
        {job.url}
      </Title>

      <Flex wrap align="center" gap={5}>
        <JobStatusTag value={job.status} completed={job.run_state} />
        <JobPriorityTag value={job.priority} />
      </Flex>

      <Space wrap style={{ marginTop: 20 }}>
        <Text strong>Status:</Text>
        <RunStateTag value={job.run_state} />
      </Space>

      <JobProgressLine job={job} size={['100%', 16]} style={{ marginTop: 8 }} />

      <Flex wrap style={{ marginTop: 5 }}>
        <Tag icon={<ClockCircleOutlined />} color="default">
          <b>Requested:</b> {formatDate(job.created_at)}
        </Tag>
        {[JobStatus.RUNNING, JobStatus.COMPLETED].includes(job.status) && (
          <Tag icon={<ClockCircleOutlined />} color="default">
            <b>Started:</b> {formatDate(job.started_at)}
          </Tag>
        )}
        {job.status === JobStatus.RUNNING && (
          <Tag icon={<ClockCircleOutlined spin />} color="default">
            <b>Elapsed:</b> {formatDuration(Date.now() - job.started_at)}
          </Tag>
        )}
        {job.status === JobStatus.COMPLETED && (
          <Tag icon={<ClockCircleFilled />} color="default">
            <b>Completed:</b> {formatDate(job.finished_at)}
          </Tag>
        )}
        {job.status === JobStatus.COMPLETED && (
          <Tag icon={<HourglassFilled />} color="default">
            <b>Runtime:</b> {formatDuration(job.finished_at - job.started_at)}
          </Tag>
        )}
      </Flex>

      {Boolean(job.error) && (
        <Alert
          showIcon
          description={job.error}
          type={job.run_state === RunState.FAILED ? 'error' : 'warning'}
          style={{ marginTop: 15, padding: '10px 20px' }}
        />
      )}

      <Flex justify="end" align="center" gap={'10px'} style={{ marginTop: 15 }}>
        <JobActionButtons job={job} />
      </Flex>
    </Card>
  );
};
