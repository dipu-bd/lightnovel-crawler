import { API_BASE_URL } from '@/config';
import { type Artifact, type Novel } from '@/types';
import { DownloadOutlined, LinkOutlined, TagOutlined } from '@ant-design/icons';
import {
  Button,
  Card,
  Col,
  Divider,
  Empty,
  Flex,
  Image,
  List,
  Row,
  Space,
  Tag,
  Typography,
} from 'antd';

const { Title, Text, Paragraph } = Typography;

export const NovelDetailsView: React.FC<{ novel?: Novel }> = ({ novel }) => {
  return (
    <Card variant="outlined" style={{ margin: 'auto', maxWidth: 1000 }}>
      {novel && !novel.orphan && novel.title ? (
        <Row gutter={[10, 20]}>
          <Col xs={24} lg={8} xxl={6} style={{ textAlign: 'center' }}>
            <Image
              alt="Novel Cover"
              src={`${API_BASE_URL}/api/novel/${novel.id}/cover`}
              style={{
                objectFit: 'cover',
                borderRadius: 8,
                maxWidth: '300px',
              }}
            />
          </Col>
          <Col xs={24} lg={16} xxl={18}>
            <Title level={4} style={{ margin: 0, color: 'inherit' }}>
              <LinkOutlined /> {novel.title}
            </Title>
            <Space style={{ margin: 5 }}>
              <Text>
                Authors: <b>{novel.authors}</b>
              </Text>
              <Divider type="vertical" />
              <Text>
                Volumes: <b>{novel.volume_count}</b>
              </Text>
              <Divider type="vertical" />
              <Text>
                Chapters: <b>{novel.chapter_count}</b>
              </Text>
            </Space>
            <Paragraph
              type="secondary"
              ellipsis={{ rows: 8 }}
              style={{ textAlign: 'justify' }}
            >
              {novel.synopsis}
            </Paragraph>
            <div style={{ marginTop: 10 }}>
              {novel.tags?.map((tag) => (
                <Tag key={tag} style={{ textTransform: 'capitalize' }}>
                  {tag.toLowerCase()}
                </Tag>
              ))}
            </div>
          </Col>
        </Row>
      ) : (
        <Empty
          image={Empty.PRESENTED_IMAGE_SIMPLE}
          description="Novel details is not available"
        />
      )}
    </Card>
  );
};

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
