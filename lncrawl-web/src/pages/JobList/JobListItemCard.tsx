import { JobPriorityTag, JobStatusTag } from '@/components/Tags/jobs';
import { Auth } from '@/store/_auth';
import { JobStatus, RunState, type Job } from '@/types';
import {
  Button,
  Card,
  Flex,
  Grid,
  message,
  Progress,
  Space,
  Typography,
} from 'antd';
import axios from 'axios';
import { useSelector } from 'react-redux';
import { Link } from 'react-router-dom';

const { Paragraph, Title } = Typography;

export const JobListItemCard: React.FC<{
  job: Job;
  onChange?: () => any;
}> = ({ job, onChange }) => {
  const { lg } = Grid.useBreakpoint();
  const isAdmin = useSelector(Auth.select.isAdmin);
  const currentUser = useSelector(Auth.select.user);

  const cancelJob = async () => {
    try {
      await axios.post(`/api/job/${job.id}/cancel`);
      onChange && onChange();
    } catch (err) {
      message.open({
        type: 'error',
        content: 'Something went wrong!',
      });
    }
  };

  return (
    <Card hoverable style={{ marginBottom: 7 }}>
      <Link to={`/job/${job.id}`}>
        <Flex wrap gap="15px" justify="end">
          {lg && (
            <Progress
              type="circle"
              percent={job.progress || 0}
              status={
                job.run_state === RunState.SUCCESS
                  ? 'success'
                  : job.run_state === RunState.FAILED
                  ? 'exception'
                  : 'active'
              }
              size="small"
            />
          )}

          <Flex
            vertical
            wrap
            gap="5px"
            style={{ flex: 1, minWidth: lg ? 0 : '100%' }}
          >
            <Paragraph
              ellipsis={{ rows: 2 }}
              style={{ marginBottom: lg ? 7 : 2 }}
            >
              <Title level={4} style={{ margin: 0 }}>
                {job.url}
              </Title>
            </Paragraph>

            {!lg && (
              <Progress
                percent={job.progress || 0}
                size={['100%', 12]}
                strokeColor={{ from: '#108ee9', to: '#87d068' }}
                status={
                  job.run_state === RunState.SUCCESS
                    ? 'success'
                    : job.run_state === RunState.FAILED
                    ? 'exception'
                    : 'active'
                }
              />
            )}

            <Space>
              <JobStatusTag value={job.status} completed={job.run_state} />
              <JobPriorityTag value={job.priority} />
            </Space>
          </Flex>

          <Flex
            justify="end"
            align="center"
            gap={'10px'}
            style={{ marginTop: 15 }}
            onClick={(e) => e.preventDefault()}
          >
            <Button danger onClick={cancelJob}>
              Cancel
            </Button>
          </Flex>

          {isAdmin || job.user_id === currentUser?.id ? (
            <Flex
              justify="end"
              align="center"
              gap={'10px'}
              style={{ marginTop: 15 }}
              onClick={(e) => e.preventDefault()}
            >
              {job.status !== JobStatus.COMPLETED && (
                <Button danger onClick={cancelJob}>
                  Cancel
                </Button>
              )}
            </Flex>
          ) : null}
        </Flex>
      </Link>
    </Card>
  );
};
