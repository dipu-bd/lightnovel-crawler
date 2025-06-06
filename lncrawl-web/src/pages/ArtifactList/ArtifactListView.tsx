import { API_BASE_URL } from '@/config';
import { type Artifact } from '@/types';
import { formatDate } from '@/utils/time';
import {
  ClockCircleOutlined,
  DownloadOutlined,
  TagOutlined,
} from '@ant-design/icons';
import { Button, Card, Empty, Flex, Grid, List, Tag, Typography } from 'antd';

const { Title, Text } = Typography;

export const ArtifactListView: React.FC<{ artifacts?: Artifact[] }> = ({
  artifacts,
}) => {
  const { sm } = Grid.useBreakpoint();
  return (
    <Card variant="outlined" style={{ margin: 'auto', maxWidth: 1000 }}>
      <Title level={4} style={{ margin: 0, marginBottom: 5 }}>
        Artifacts
      </Title>
      {artifacts && artifacts.length > 0 ? (
        <List
          dataSource={artifacts}
          renderItem={(item) => (
            <List.Item
              actions={[
                <Button
                  type="primary"
                  target="_blank"
                  icon={<DownloadOutlined />}
                  href={`${API_BASE_URL}/api/artifact/${item.id}/download`}
                  rel="noopener noreferrer"
                  style={{ margin: 5 }}
                >
                  {sm ? 'Download' : ''}
                </Button>,
              ]}
            >
              <List.Item.Meta
                title={
                  <Flex gap={8} align="center">
                    <Tag icon={<TagOutlined />} style={{ margin: 0 }}>
                      {item.format}
                    </Tag>
                    <Text
                      ellipsis
                      style={{ fontWeight: 'normal', fontSize: 12 }}
                    >
                      <ClockCircleOutlined /> {formatDate(item.updated_at)}
                    </Text>
                  </Flex>
                }
                description={item.file_name}
              />
            </List.Item>
          )}
        />
      ) : (
        <Empty
          image={Empty.PRESENTED_IMAGE_SIMPLE}
          description="No artifacts"
        />
      )}
    </Card>
  );
};
