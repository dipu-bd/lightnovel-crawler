import type { Job } from '@/types';
import { stringifyError } from '@/utils/errors';
import { Alert, Button, Card, Flex, Form, Input, Typography } from 'antd';
import FormItem from 'antd/es/form/FormItem';
import axios from 'axios';
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

export const HomePage: React.FC<any> = () => {
  const [form] = Form.useForm();
  const navigate = useNavigate();
  const [error, setError] = useState<string>();
  const [loading, setLoading] = useState<boolean>(false);

  const submitJob = async (values: any) => {
    setLoading(true);
    setError(undefined);
    try {
      const result = await axios.post<Job>(
        `/api/job`,
        new URLSearchParams(values).toString(),
        {
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
          },
        }
      );
      navigate({ pathname: `/job/${result.data.id}` });
    } catch (err) {
      setError(stringifyError(err, 'Oops! Something went wrong.'));
    } finally {
      setLoading(false);
    }
  };

  return (
    <Flex
      align="center"
      justify="center"
      style={{ width: '100%', height: '100%' }}
    >
      <Card
        title={
          <Typography.Title level={3} style={{ margin: 0 }}>
            Request Novel
          </Typography.Title>
        }
        style={{ width: '650px' }}
      >
        <Form
          form={form}
          size="large"
          onFinish={submitJob}
          labelCol={{ style: { padding: 0 } }}
          encType="application/x-www-form-urlencoded"
        >
          <Form.Item name="url" rules={[{ required: true, type: 'url' }]}>
            <Input
              placeholder="Enter novel page url"
              autoComplete="novel-page-url"
            />
          </Form.Item>
          <Typography.Text type="secondary">
            A novel page URL should contain the novel details, e.g. title, cover
            image author, synopsis etc. Note that partial URLs are not accepted.
            The URL should start with http:// or https://
          </Typography.Text>

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
              children={'Submit'}
            />
          </FormItem>
        </Form>
      </Card>
    </Flex>
  );
};

export default HomePage;
