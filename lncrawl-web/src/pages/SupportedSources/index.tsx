import { Button, Flex, Result, Space, Spin, Tabs, Typography } from 'antd';
import { SupportedSourceList } from './SupportedSourceList';
import { useSupportedSources } from './hooks';
import { useMemo } from 'react';

export const SupportedSourcesPage: React.FC<any> = () => {
  const { data, loading, error, refresh } = useSupportedSources();

  const active = useMemo(() => data.filter((x) => !x.is_disabled), [data]);
  const disabled = useMemo(() => data.filter((x) => x.is_disabled), [data]);

  if (loading) {
    return (
      <Flex align="center" justify="center" style={{ height: '100%' }}>
        <Spin size="large" style={{ marginTop: 100 }} />
      </Flex>
    );
  }

  if (error) {
    return (
      <Flex align="center" justify="center" style={{ height: '100%' }}>
        <Result
          status="error"
          title="Failed to load novel list"
          subTitle={error}
          extra={[<Button onClick={refresh}>Retry</Button>]}
        />
      </Flex>
    );
  }
  return (
    <Tabs defaultActiveKey="active" style={{ padding: 15 }} tabBarGutter={20}>
      <Tabs.TabPane
        key="active"
        tab={
          <Space>
            <Typography.Text strong>Active Sources</Typography.Text>
            <small>
              <code>{active.length}</code>
            </small>
          </Space>
        }
      >
        <SupportedSourceList sources={active} />
      </Tabs.TabPane>
      <Tabs.TabPane
        key="disabled"
        tab={
          <Space>
            <Typography.Text strong>Disabled Sources</Typography.Text>
            <small>
              <code>{disabled.length}</code>
            </small>
          </Space>
        }
      >
        <SupportedSourceList sources={disabled} disabled />
      </Tabs.TabPane>
    </Tabs>
  );
};
