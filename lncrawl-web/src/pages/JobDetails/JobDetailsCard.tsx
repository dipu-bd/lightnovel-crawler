import {
  JobPriorityTag,
  JobStatusTag,
  RunStateTag,
} from '@/components/Tags/jobs';
import { RunState, type Job } from '@/types';
import { calculateRemaining, formatDate, formatDuration } from '@/utils/time';
import {
  ClockCircleFilled,
  ClockCircleOutlined,
  HourglassFilled,
} from '@ant-design/icons';
import {
  Alert,
  Card,
  Flex,
  Grid,
  Progress,
  Space,
  Tag,
  Typography,
} from 'antd';
import { JobActionButtons } from '../JobList/JobActionButtons';

const { Title, Text } = Typography;

export const JobDetailsCard: React.FC<{ job: Job }> = ({ job }) => {
  const { lg } = Grid.useBreakpoint();

  return (
    <Card variant="outlined" style={{ margin: 'auto', maxWidth: 1000 }}>
      <Title level={3} style={{ margin: 0, marginBottom: 8 }}>
        {job.url}
      </Title>

      <Flex wrap align="center" gap={5}>
        <JobStatusTag value={job.status} completed={job.run_state} />
        <JobPriorityTag value={job.priority} />
        {lg && (
          <Tag
            icon={<ClockCircleOutlined />}
            color="default"
            style={{ margin: 0 }}
          >
            {formatDate(job.created_at)}
          </Tag>
        )}
      </Flex>

      <Space wrap style={{ marginTop: 20 }}>
        <Text strong>Status:</Text>
        <RunStateTag value={job.run_state} />
      </Space>

      <Progress
        percent={job.progress || 0}
        size={['100%', 16]}
        strokeColor={{ from: '#108ee9', to: '#87d068' }}
        status={
          job.run_state === RunState.SUCCESS
            ? 'success'
            : job.run_state === RunState.FAILED
            ? 'exception'
            : 'active'
        }
        style={{ marginTop: 8 }}
      />

      <Flex wrap style={{ marginTop: 5 }}>
        {job.started_at > 0 && (
          <Tag icon={<ClockCircleOutlined />} color="default">
            <b>Started:</b> {formatDate(job.started_at)}
          </Tag>
        )}
        {job.finished_at > 0 ? (
          <>
            <Tag icon={<ClockCircleFilled />} color="default">
              <b>Completed:</b> {formatDate(job.finished_at)}
            </Tag>
            <Tag icon={<HourglassFilled />} color="default">
              <b>Runtime:</b> {formatDuration(job.finished_at - job.started_at)}
            </Tag>
          </>
        ) : (
          <>
            <Tag icon={<ClockCircleOutlined spin />} color="default">
              <b>Elapsed:</b> {formatDuration(Date.now() - job.started_at)}
            </Tag>
            <Tag icon={<ClockCircleOutlined spin />} color="default">
              <b>Estimated:</b>{' '}
              {calculateRemaining(job.started_at, job.progress)}
            </Tag>
          </>
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
