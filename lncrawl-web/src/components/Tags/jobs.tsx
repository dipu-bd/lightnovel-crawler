import { JobPriority, JobStatus, RunState } from '@/types';
import {
  CheckOutlined,
  CloseOutlined,
  HourglassOutlined,
  LoadingOutlined,
  ThunderboltOutlined,
  WarningOutlined,
} from '@ant-design/icons';
import { Tag } from 'antd';

export const JobPriorityTag: React.FC<{ value: JobPriority }> = ({ value }) => {
  switch (value) {
    case JobPriority.LOW:
      return (
        <Tag icon={<ThunderboltOutlined />} style={{ margin: 0 }}>
          Low Priority
        </Tag>
      );
    case JobPriority.NORMAL:
      return (
        <Tag icon={<ThunderboltOutlined />} color="gold" style={{ margin: 0 }}>
          Normal Priority
        </Tag>
      );
    case JobPriority.HIGH:
      return (
        <Tag
          icon={<ThunderboltOutlined />}
          color="volcano"
          style={{ margin: 0 }}
        >
          <b>High Priority</b>
        </Tag>
      );
  }
};

export const JobStatusTag: React.FC<{
  value: JobStatus;
  completed: RunState;
}> = ({ value, completed }) => {
  switch (value) {
    case JobStatus.PENDING:
      return (
        <Tag icon={<HourglassOutlined />} style={{ margin: 0 }}>
          Pending
        </Tag>
      );
    case JobStatus.RUNNING:
      return (
        <Tag icon={<LoadingOutlined spin />} color="cyan" style={{ margin: 0 }}>
          Running
        </Tag>
      );
    case JobStatus.COMPLETED: {
      switch (completed) {
        case RunState.SUCCESS:
          return (
            <Tag icon={<CheckOutlined />} color="orange" style={{ margin: 0 }}>
              Success
            </Tag>
          );
        case RunState.CANCELED:
          return (
            <Tag icon={<CloseOutlined />} color="red" style={{ margin: 0 }}>
              Canceled
            </Tag>
          );
        case RunState.FAILED:
          return (
            <Tag icon={<WarningOutlined />} color="red" style={{ margin: 0 }}>
              Failed
            </Tag>
          );
        default:
          return (
            <Tag icon={<CheckOutlined />} color="orange" style={{ margin: 0 }}>
              Completed
            </Tag>
          );
      }
    }
    default:
      return null;
  }
};

export const RunStateTag: React.FC<{ value: RunState }> = ({ value }) => {
  switch (value) {
    case RunState.FETCHING_NOVEL:
      return <span>Fetching novel details</span>;
    case RunState.FETCHING_CONTENT:
      return <span>Fetching novel contents</span>;
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
