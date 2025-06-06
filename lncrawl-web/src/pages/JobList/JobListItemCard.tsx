import { JobPriorityTag, JobStatusTag } from '@/components/Tags/jobs';
import { Auth } from '@/store/_auth';
import { JobStatus, RunState, type Job } from '@/types';
import { formatDate } from '@/utils/time';
import { ClockCircleOutlined } from '@ant-design/icons';
import { Button, Card, Flex, message, Progress, Tag, Typography } from 'antd';
import axios from 'axios';
import { useSelector } from 'react-redux';
import { Link } from 'react-router-dom';

const { Paragraph, Title } = Typography;

export const JobListItemCard: React.FC<{
  job: Job;
  onChange?: () => any;
}> = ({ job, onChange }) => {
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
        <Flex gap="15px">
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

          <div style={{ flex: 1, minWidth: 0 }}>
            <Paragraph ellipsis={{ rows: 2 }}>
              <Title level={4} style={{ margin: 0 }}>
                {job.url}
              </Title>
            </Paragraph>
            <JobStatusTag value={job.status} completed={job.run_state} />
            <JobPriorityTag value={job.priority} />
            <Tag icon={<ClockCircleOutlined />} color="default">
              {formatDate(job.created_at)}
            </Tag>
          </div>

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
