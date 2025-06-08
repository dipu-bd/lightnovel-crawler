import { store } from '@/store';
import { Auth } from '@/store/_auth';
import { stringifyError } from '@/utils/errors';
import { LoginOutlined } from '@ant-design/icons';
import {
  Alert,
  Avatar,
  Button,
  Card,
  Divider,
  Flex,
  Form,
  Input,
  Layout,
  Space,
  Typography,
} from 'antd';
import FormItem from 'antd/es/form/FormItem';
import axios from 'axios';
import { useState } from 'react';

export const SignupPage: React.FC<any> = () => {
  const [form] = Form.useForm();
  const [error, setError] = useState<string>();
  const [loading, setLoading] = useState<boolean>(false);

  const handleSignup = async (data: any) => {
    setLoading(true);
    setError(undefined);
    try {
      const result = await axios.post(`/api/auth/signup`, data);
      store.dispatch(Auth.action.setAuth(result.data));
    } catch (err) {
      setError(stringifyError(err, 'Oops! Something went wrong.'));
    } finally {
      setLoading(false);
    }
  };

  return (
    <Layout
      style={{
        padding: '10px',
        overflow: 'auto',
        height: 'calc(100vh - 40px)',
      }}
    >
      <Layout.Content style={{ overflow: 'auto' }}>
        <Flex
          align="center"
          justify="center"
          style={{ width: '100%', height: '100%' }}
        >
          <Card
            title={
              <Space
                direction="vertical"
                align="center"
                style={{ padding: '15px', width: '100%' }}
              >
                <Avatar
                  src="/lncrawl.svg"
                  style={{ width: '96px', height: '96px' }}
                />
                <Typography.Title
                  type="success"
                  level={3}
                  style={{ margin: 0 }}
                >
                  Lightnovel Crawler
                </Typography.Title>
              </Space>
            }
            style={{ width: '400px' }}
          >
            <Form
              form={form}
              onFinish={handleSignup}
              size="large"
              layout="vertical"
              labelCol={{ style: { padding: 0 } }}
            >
              <Form.Item name="name" label="Full Name">
                <Input placeholder="Enter full name" autoComplete="name" />
              </Form.Item>
              <Form.Item
                name="email"
                label="Email"
                rules={[{ required: true }]}
              >
                <Input placeholder="Enter email" autoComplete="new-user" />
              </Form.Item>
              <Form.Item
                name={'password'}
                label="Password"
                rules={[{ required: true }]}
              >
                <Input.Password
                  placeholder="Enter password"
                  autoComplete="new-password"
                />
              </Form.Item>

              {Boolean(error) && (
                <Alert
                  type="warning"
                  showIcon
                  message={error}
                  closable
                  onClose={() => setError('')}
                />
              )}

              <FormItem style={{ marginTop: '20px' }}>
                <Button
                  block
                  type="primary"
                  htmlType="submit"
                  loading={loading}
                  disabled={loading}
                  icon={<LoginOutlined />}
                  children={'Register'}
                />
              </FormItem>
            </Form>

            <Divider />

            <Flex justify="center">
              <Typography.Link href="/login">
                Use existing account
              </Typography.Link>
            </Flex>
          </Card>
        </Flex>
      </Layout.Content>
    </Layout>
  );
};
