import { JobPriorityTag, JobStatusTag } from '@/components/Tags/jobs';
import { type Job } from '@/types';
import { Card, Flex, Grid, Space, Typography } from 'antd';
import { Link } from 'react-router-dom';
import { JobActionButtons } from './JobActionButtons';
import { JobProgressCircle, JobProgressLine } from './JobProgessBar';

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
          {lg && <JobProgressCircle job={job} />}

          <div style={{ flex: 1, minWidth: lg ? 0 : '100%' }}>
            <Typography.Paragraph
              ellipsis={{ rows: 2 }}
              style={{
                fontSize: '1.15rem',
                fontFamily: "'Roboto Slab', serif",
              }}
            >
              {job.url}
            </Typography.Paragraph>

            <Space style={{ marginTop: 5 }}>
              <JobStatusTag value={job.status} completed={job.run_state} />
              <JobPriorityTag value={job.priority} />
            </Space>

            {!lg && <JobProgressLine job={job} style={{ marginTop: 10 }} />}
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
