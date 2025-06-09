import { JobStatus, RunState, type Job } from '@/types';
import { Progress, type ProgressProps } from 'antd';

function getProgressStatus(job: Job): ProgressProps['status'] {
  switch (job.status) {
    case JobStatus.PENDING:
    case JobStatus.RUNNING:
      return 'active';
    case JobStatus.COMPLETED:
      switch (job.run_state) {
        case RunState.SUCCESS:
          return 'success';
        case RunState.FAILED:
        case RunState.CANCELED:
          return 'exception';
      }
  }
  return 'normal';
}

export const JobProgressCircle: React.FC<
  {
    job: Job;
  } & ProgressProps
> = ({ job, ...props }) => {
  return (
    <Progress
      size="small"
      {...props}
      type="circle"
      percent={job.progress || 0}
      status={getProgressStatus(job)}
    />
  );
};

export const JobProgressLine: React.FC<
  {
    job: Job;
  } & ProgressProps
> = ({ job, ...props }) => {
  return (
    <Progress
      size={['100%', 12]}
      {...props}
      type="line"
      percent={job.progress || 0}
      status={getProgressStatus(job)}
      strokeColor={{ from: '#108ee9', to: '#87d068' }}
    />
  );
};
