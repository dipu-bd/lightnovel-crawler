import { API_BASE_URL } from '@/config';
import { type Artifact } from '@/types';
import { DownloadOutlined, TagOutlined } from '@ant-design/icons';
import { Button, Card, Empty, Flex, List, Tag, Typography } from 'antd';

const { Title, Text } = Typography;

export const ArtifactListView: React.FC<{ artifacts?: Artifact[] }> = ({
  artifacts,
}) => {
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
                >
                  Download
                </Button>,
              ]}
            >
              <List.Item.Meta
                title={
                  <Flex>
                    <Flex style={{ width: '75px' }}>
                      <Tag icon={<TagOutlined />}>{item.format}</Tag>
                    </Flex>
                    <Text ellipsis title={item.file_name}>
                      {item.file_name}
                    </Text>
                  </Flex>
                }
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
