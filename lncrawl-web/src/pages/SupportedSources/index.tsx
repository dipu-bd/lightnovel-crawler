import {
  Badge,
  Button,
  Flex,
  Result,
  Space,
  Spin,
  Tabs,
  Typography,
} from 'antd';
import { SupportedSourceList } from './SupportedSourceList';
import { useSupportedSources } from './hooks';

const { Text } = Typography;

export default function SupportedSourcesPage() {
  const { data, loading, error, refresh } = useSupportedSources();

  const active = data.filter((x) => !x.is_disabled);
  const disabled = data.filter((x) => x.is_disabled);

  if (loading) {
    return (
      <Flex align="center" justify="center" style={{ height: '100%' }}>
        <Spin tip="Loading job..." size="large" style={{ marginTop: 100 }} />
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
            <Text strong>Active Sources</Text>
            <Badge color="blue" count={active.length} />
          </Space>
        }
      >
        <SupportedSourceList sources={active} />
      </Tabs.TabPane>
      <Tabs.TabPane
        key="disabled"
        tab={
          <Space>
            <Text strong>Disabled Sources</Text>
            <Badge color="magenta" count={disabled.length} />
          </Space>
        }
      >
        <SupportedSourceList sources={disabled} disabled />
      </Tabs.TabPane>
    </Tabs>
  );
}
