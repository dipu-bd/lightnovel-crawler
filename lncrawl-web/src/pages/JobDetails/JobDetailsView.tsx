import {
  JobPriorityTag,
  JobStatusTag,
  RunStateTag,
} from '@/components/Tags/jobs';
import { Auth } from '@/store/_auth';
import { JobStatus, RunState, type Job } from '@/types';
import { formatDate, formatDuration } from '@/utils/time';
import {
  ClockCircleFilled,
  ClockCircleOutlined,
  HourglassFilled,
} from '@ant-design/icons';
import {
  Button,
  Card,
  Flex,
  Grid,
  message,
  Progress,
  Space,
  Tag,
  Typography,
} from 'antd';
import axios from 'axios';
import { useSelector } from 'react-redux';

const { Title, Text } = Typography;

export const JobDetailsView: React.FC<{ job: Job }> = ({ job }) => {
  const { lg } = Grid.useBreakpoint();
  const isAdmin = useSelector(Auth.select.isAdmin);
  const currentUser = useSelector(Auth.select.user);

  const cancelJob = async () => {
    try {
      await axios.post(`/api/job/${job.id}/cancel`);
    } catch (err) {
      message.open({
        type: 'error',
        content: 'Something went wrong!',
      });
    }
  };

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
        {job.finished_at > 0 && (
          <>
            <Tag icon={<ClockCircleFilled />} color="default">
              <b>Completed:</b> {formatDate(job.finished_at)}
            </Tag>
            <Tag icon={<HourglassFilled />} color="default">
              <b>Runtime:</b> {formatDuration(job.finished_at - job.started_at)}
            </Tag>
          </>
        )}
      </Flex>

      {isAdmin || job.user_id === currentUser?.id ? (
        <Flex
          justify="end"
          align="center"
          gap={'10px'}
          style={{ marginTop: 15 }}
        >
          {job.status !== JobStatus.COMPLETED && (
            <Button danger onClick={cancelJob}>
              Cancel Job
            </Button>
          )}
        </Flex>
      ) : null}
    </Card>
  );
};
