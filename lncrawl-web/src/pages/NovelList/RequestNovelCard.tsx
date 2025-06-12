import type { Job } from '@/types';
import { stringifyError } from '@/utils/errors';
import { SendOutlined } from '@ant-design/icons';
import { Alert, Button, Form, Grid, Input, Typography } from 'antd';
import axios from 'axios';
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

const { Text } = Typography;

export const RequestNovelCard: React.FC<any> = () => {
  const { lg } = Grid.useBreakpoint();

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
    <Form
      form={form}
      size="large"
      onFinish={submitJob}
      labelCol={{ style: { padding: 0 } }}
      encType="application/x-www-form-urlencoded"
    >
      {Boolean(error) && (
        <Alert
          type="warning"
          showIcon
          message={error}
          closable
          onClose={() => setError('')}
          style={{ marginTop: '15px' }}
        />
      )}
      <Form.Item name="url" rules={[{ required: true, type: 'url' }]}>
        <div style={{ position: 'relative' }}>
          <Input.TextArea
            rows={1}
            autoSize
            autoFocus
            placeholder="Enter novel page URL"
            autoComplete="novel-page-url"
            onInput={(e) => {
              const value = e.currentTarget.value;
              const trimmed = value.replace(/[\n\r\t ]+/g, '');
              if (trimmed !== value) {
                e.currentTarget.value = trimmed;
              }
            }}
            style={{
              resize: 'none',
              fontWeight: '800',
              fontFamily: "'Roboto Slab', serif",
              fontSize: lg ? '1.4rem' : '1.25rem',
              paddingRight: lg ? 125 : 50,
              outline: 'none',
              minHeight: 50,
              borderRadius: 0,
              letterSpacing: 1.01,
            }}
            styles={{
              textarea: {
                overflow: 'hidden',
                scrollbarWidth: 'none',
                msOverflowStyle: 'none',
              },
            }}
            onPressEnter={(e) => {
              e.preventDefault();
              form.submit();
            }}
          />
          <Button
            type="primary"
            htmlType="submit"
            loading={loading}
            icon={<SendOutlined />}
            children={lg ? 'Submit' : ''}
            style={{
              height: 43,
              position: 'absolute',
              right: 3,
              bottom: 4,
              zIndex: 2,
              padding: lg ? 18 : '0 15px',
              fontSize: lg ? '1.25rem' : '1rem',
              borderRadius: 0,
            }}
          />
        </div>
      </Form.Item>

      <Text type="secondary">
        Enter the full URL of the novel page. The URL must begin with 'http://'
        or 'https://' and should lead to a page containing the novel details
        such as title, cover image, author, synopsis, chapter list etc. Partial
        or incomplete URLs will not be accepted.
      </Text>
    </Form>
  );
};
