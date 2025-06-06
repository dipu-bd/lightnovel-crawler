import { JobPriorityTag, JobStatusTag } from '@/components/Tags/jobs';
import { RunState, type Job } from '@/types';
import { Card, Flex, Grid, Progress, Space, Typography } from 'antd';
import { Link } from 'react-router-dom';
import { JobActionButtons } from './JobActionButtons';

const { Paragraph, Title } = Typography;

export const JobListItemCard: React.FC<{
  job: Job;
  onChange?: () => any;
}> = ({ job, onChange }) => {
  const { lg } = Grid.useBreakpoint();

  return (
    <Card hoverable style={{ marginBottom: 7 }}>
      <Link to={`/job/${job.id}`}>
        <Flex wrap gap="15px" justify="end">
          {lg && (
            <Progress
              type="circle"
              size="small"
              percent={job.progress || 0}
              status={
                job.run_state === RunState.SUCCESS
                  ? 'success'
                  : job.run_state === RunState.FAILED
                  ? 'exception'
                  : 'active'
              }
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
            wrap
            justify="end"
            align="center"
            gap={5}
            onClick={(e) => e.preventDefault()}
          >
            <JobActionButtons job={job} onChange={onChange} />
          </Flex>
        </Flex>
      </Link>
    </Card>
  );
};
