import { store } from '@/store';
import { Auth } from '@/store/_auth';
import { stringifyError } from '@/utils/errors';
import { LogoutOutlined, WarningOutlined } from '@ant-design/icons';
import {
  Alert,
  Button,
  Flex,
  Input,
  message,
  Modal,
  Space,
  Typography,
} from 'antd';
import axios from 'axios';
import { useEffect, useState } from 'react';
import { useSelector } from 'react-redux';
import { UserAvatar } from '../Tags/gravatar';

export const UserInfoCard: React.FC<any> = () => {
  const [messageApi, contextHolder] = message.useMessage();
  const [showVerify, setShowVerify] = useState<boolean>(false);

  const [otp, setOtp] = useState<string>('');
  const [token, setToken] = useState<string>();
  const [resendTimeout, setResendTimeout] = useState<number>(0);

  const [error, setError] = useState<string>();
  const [loading, setLoading] = useState<boolean>(false);

  const authUser = useSelector(Auth.select.user);
  const isVerified = useSelector(Auth.select.isVerified);

  useEffect(() => {
    if (resendTimeout <= 0) return;
    const tid = setTimeout(() => {
      setResendTimeout((v) => v - 1);
    }, 998);
    return () => clearTimeout(tid);
  }, [resendTimeout]);

  const handleLogout = () => {
    store.dispatch(Auth.action.clearAuth());
  };

  const sendOTP = async () => {
    try {
      setError(undefined);
      setLoading(true);
      setResendTimeout(30);
      const { data } = await axios.post('/api/auth/me/send-otp');
      setToken(data.token);
    } catch (err) {
      setError(stringifyError(err));
    } finally {
      setLoading(false);
    }
  };

  const startVerifyEmail = async () => {
    if (!loading && resendTimeout <= 0) {
      sendOTP();
    }
    setShowVerify(true);
  };

  const handleVerify = async () => {
    try {
      if (!token || !otp) {
        return;
      }
      await axios.post(
        `/api/auth/me/verify-otp`,
        new URLSearchParams({ otp, token }).toString(),
        {
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
          },
        }
      );
      store.dispatch(Auth.action.setEmailVerified());
      setShowVerify(false);
      messageApi.open({
        type: 'success',
        content: 'Awesome! Your email is now verified.',
      });
    } catch (err) {
      messageApi.open({
        type: 'error',
        content: stringifyError(err),
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Flex
      vertical
      gap="5px"
      align="center"
      justify="center"
      style={{
        textAlign: 'center',
        paddingTop: '25px',
        paddingBottom: '10px',
      }}
    >
      <UserAvatar
        size={72}
        user={authUser}
        style={{ backgroundColor: 'blueviolet' }}
      />
      <Typography.Text strong>{authUser?.name}</Typography.Text>

      <div />

      {!isVerified && (
        <Button
          block
          danger
          shape="round"
          onClick={startVerifyEmail}
          icon={<WarningOutlined />}
          children="Verify Email"
        />
      )}

      <div />
      <div />

      <Button
        block
        type="default"
        onClick={handleLogout}
        icon={<LogoutOutlined />}
        children="Logout"
      />

      <Modal
        centered
        open={showVerify}
        maskClosable={false}
        title="Verify Email"
        okText="Verify"
        width={450}
        onOk={handleVerify}
        onCancel={() => setShowVerify(false)}
        cancelButtonProps={{ type: 'text' }}
        okButtonProps={{ loading, disabled: !otp || !token }}
      >
        {contextHolder}
        <Flex vertical gap={15}>
          <Typography.Text>
            A 6-digit verification code was sent to your email address. Please
            enter the code below to continue.
          </Typography.Text>

          <Input.OTP length={6} value={otp} onChange={setOtp} size="large" />

          <Space>
            <Typography.Text>Did not receive the OTP?</Typography.Text>
            {resendTimeout > 0 ? (
              <Typography.Text type="secondary">
                You can send again in {resendTimeout} seconds.
              </Typography.Text>
            ) : (
              <Typography.Link onClick={sendOTP}>
                Click here to send again.
              </Typography.Link>
            )}
          </Space>

          {Boolean(error) && <Alert type="error" showIcon message={error} />}
        </Flex>
      </Modal>
    </Flex>
  );
};
