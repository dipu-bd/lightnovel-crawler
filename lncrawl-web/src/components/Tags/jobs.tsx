import { JobPriority, JobStatus, RunState } from '@/types';
import {
  CheckOutlined,
  HourglassOutlined,
  LoadingOutlined,
  ThunderboltOutlined,
} from '@ant-design/icons';
import { Tag } from 'antd';

export const JobPriorityTag: React.FC<{ value: JobPriority }> = ({ value }) => {
  switch (value) {
    case JobPriority.LOW:
      return <Tag icon={<ThunderboltOutlined />}>Low Priority</Tag>;
    case JobPriority.NORMAL:
      return (
        <Tag icon={<ThunderboltOutlined />} color="gold">
          Normal Priority
        </Tag>
      );
    case JobPriority.HIGH:
      return (
        <Tag icon={<ThunderboltOutlined />} color="volcano">
          <b>High Priority</b>
        </Tag>
      );
  }
};

export const JobStatusTag: React.FC<{ value: JobStatus }> = ({ value }) => {
  switch (value) {
    case JobStatus.PENDING:
      return <Tag icon={<HourglassOutlined />}>Pending</Tag>;
    case JobStatus.RUNNING:
      return (
        <Tag icon={<LoadingOutlined spin />} color="cyan">
          Running
        </Tag>
      );
    case JobStatus.COMPLETED:
      return (
        <Tag icon={<CheckOutlined />} color="orange">
          Completed
        </Tag>
      );
    default:
      return null;
  }
};

export const RunStateTag: React.FC<{ value: RunState }> = ({ value }) => {
  switch (value) {
    case RunState.FETCHING_NOVEL:
      return <span>Fetching novel details</span>;
    case RunState.FETCHING_CHAPTERS:
      return <span>Fetching all chapter contents</span>;
    case RunState.FETCHING_IMAGES:
      return <span>Fetching novel color and chapter images</span>;
    case RunState.CREATING_ARTIFACTS:
      return <span>Binding books and uploading artifacts</span>;
    case RunState.SUCCESS:
      return <span>Success</span>;
    case RunState.FAILED:
      return <span>Failed</span>;
    case RunState.CANCELED:
      return <span>Canceled</span>;
    default:
      return null;
  }
};
