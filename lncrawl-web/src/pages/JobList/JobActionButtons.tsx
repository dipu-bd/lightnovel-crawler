import { Auth } from '@/store/_auth';
import { JobStatus, type Job } from '@/types';
import { stringifyError } from '@/utils/errors';
import { CloseOutlined, ReloadOutlined } from '@ant-design/icons';
import { Button, message } from 'antd';
import axios from 'axios';
import { useSelector } from 'react-redux';
import { useNavigate } from 'react-router-dom';

export const JobActionButtons: React.FC<{
  job: Job;
  onChange?: () => any;
}> = ({ job, onChange }) => {
  const navigate = useNavigate();
  const isAdmin = useSelector(Auth.select.isAdmin);
  const currentUser = useSelector(Auth.select.user);

  const cancelJob = async () => {
    try {
      await axios.post(`/api/job/${job.id}/cancel`);
      if (onChange) onChange();
    } catch (err) {
      message.open({
        type: 'error',
        content: stringifyError(err, 'Something went wrong!'),
      });
    }
  };

  const replayJob = async () => {
    try {
      const result = await axios.post<Job>(
        `/api/job`,
        new URLSearchParams({ url: job.url }).toString(),
        {
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
          },
        }
      );
      navigate({ pathname: `/job/${result.data.id}` });
    } catch (err) {
      message.open({
        type: 'error',
        content: stringifyError(err, 'Something went wrong!'),
      });
    }
  };

  return (
    <>
      {job.status === JobStatus.COMPLETED && (
        <Button onClick={replayJob}>
          <ReloadOutlined /> Replay
        </Button>
      )}
      {(isAdmin || job.user_id === currentUser?.id) &&
        job.status !== JobStatus.COMPLETED && (
          <Button danger onClick={cancelJob}>
            <CloseOutlined /> Cancel
          </Button>
        )}
    </>
  );
};
