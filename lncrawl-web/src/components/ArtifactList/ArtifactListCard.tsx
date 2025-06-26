import { API_BASE_URL } from '@/config';
import { type Artifact } from '@/types';
import { formatFileSize } from '@/utils/size';
import { formatDate } from '@/utils/time';
import {
  ClockCircleOutlined,
  DownloadOutlined,
  ExclamationCircleOutlined,
  FileZipFilled,
  TagOutlined,
} from '@ant-design/icons';
import {
  Button,
  Card,
  Empty,
  Flex,
  Grid,
  List,
  Tag,
  Tooltip,
  Typography,
} from 'antd';

export const ArtifactListCard: React.FC<{ artifacts?: Artifact[] }> = ({
  artifacts,
}) => {
  const { sm } = Grid.useBreakpoint();
  return (
    <Card title="Artifacts" variant="outlined">
      {artifacts && artifacts.length > 0 ? (
        <List
          dataSource={artifacts}
          renderItem={(item) => (
            <List.Item
              actions={
                item.is_available
                  ? [
                      <Button
                        type="primary"
                        target="_blank"
                        icon={<DownloadOutlined />}
                        href={`${API_BASE_URL}/api/artifact/${item.id}/download`}
                        rel="noopener noreferrer"
                        style={{ margin: 5, fontSize: sm ? '15px' : '1.2rem' }}
                      >
                        {sm ? 'Download' : ''}
                      </Button>,
                    ]
                  : [
                      <Tooltip title="The file is no longer available">
                        <Button disabled icon={<ExclamationCircleOutlined />}>
                          {sm ? 'Download' : ''}
                        </Button>
                      </Tooltip>,
                    ]
              }
            >
              <List.Item.Meta
                description={
                  item.is_available ? item.file_name : <s>{item.file_name}</s>
                }
                title={
                  <Flex wrap="wrap-reverse" gap={8} align="center">
                    <Tag icon={<TagOutlined />} style={{ margin: 0 }}>
                      {item.format}
                    </Tag>
                    {Boolean(item.file_size && item.file_size > 0) && (
                      <Typography.Text
                        type="warning"
                        style={{
                          whiteSpace: 'nowrap',
                          fontWeight: 'normal',
                          fontSize: 12,
                        }}
                      >
                        <FileZipFilled /> {formatFileSize(item.file_size)}
                      </Typography.Text>
                    )}
                    <Typography.Text
                      ellipsis
                      style={{ fontWeight: 'normal', fontSize: 12 }}
                    >
                      <ClockCircleOutlined /> {formatDate(item.updated_at)}
                    </Typography.Text>
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
