import { JobPriorityTag, JobStatusTag } from '@/components/Tags/jobs';
import { RunState, type Job } from '@/types';
import { Card, Flex, Grid, Progress, Space, Typography } from 'antd';
import { Link } from 'react-router-dom';
import { JobActionButtons } from './JobActionButtons';

const { Paragraph } = Typography;

export const JobListItemCard: React.FC<{
  job: Job;
  onChange?: () => any;
}> = ({ job, onChange }) => {
  const { lg } = Grid.useBreakpoint();
  return (
    <Link to={`/job/${job.id}`}>
      <Card
        hoverable
        style={{ marginBottom: 5 }}
        styles={{
          body: { padding: lg ? undefined : 15 },
        }}
      >
        <Flex wrap align="center" justify="end" gap="15px">
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

          <div style={{ flex: 1, minWidth: lg ? 0 : '100%' }}>
            <Paragraph
              ellipsis={{ rows: 2 }}
              style={{
                fontSize: '1.15rem',
                fontFamily: "'Roboto Slab', serif",
              }}
            >
              {job.url}
            </Paragraph>

            <Space style={{ marginTop: 5 }}>
              <JobStatusTag value={job.status} completed={job.run_state} />
              <JobPriorityTag value={job.priority} />
            </Space>

            {!lg && (
              <Progress
                percent={job.progress || 0}
                size={['100%', 12]}
                strokeColor={{ from: '#108ee9', to: '#87d068' }}
                style={{ marginTop: 10 }}
                status={
                  job.run_state === RunState.SUCCESS
                    ? 'success'
                    : job.run_state === RunState.FAILED
                    ? 'exception'
                    : 'active'
                }
              />
            )}
          </div>

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
      </Card>
    </Link>
  );
};
