import { UserAvatar } from '@/components/Tags/gravatar';
import {
  UserRoleTag,
  UserStatusTag,
  UserTierTag,
} from '@/components/Tags/users';
import { type User } from '@/types';
import { formatDate } from '@/utils/time';
import { CalendarOutlined } from '@ant-design/icons';
import { Card, Col, Flex, Row, Space, Typography } from 'antd';

export const UserDetailsCard: React.FC<{ user: User }> = ({ user }) => {
  return (
    <Card variant="outlined">
      <Typography.Title level={4} style={{ margin: 0, marginBottom: 16 }}>
        Initiated By
      </Typography.Title>

      <Row align="middle" gutter={[16, 16]}>
        <Col flex="auto">
          <Space size="middle">
            <UserAvatar
              size={56}
              user={user}
              style={{ backgroundColor: '#1890ff' }}
            />
            <Flex vertical>
              <Typography.Title level={5} style={{ margin: 0 }}>
                {user.name || 'Unknown User'}
              </Typography.Title>
              {/* <Text type="secondary">{user.email}</Text> */}
            </Flex>
          </Space>
        </Col>

        <Col flex="auto">
          <Flex wrap gap="10px" justify="space-between">
            <Flex wrap vertical gap="10px">
              <Flex gap="10px">
                <Typography.Text
                  strong
                  style={{ width: 70, textAlign: 'right' }}
                >
                  Role:
                </Typography.Text>
                <UserRoleTag value={user.role} />
              </Flex>
              <Flex gap="10px">
                <Typography.Text
                  strong
                  style={{ width: 70, textAlign: 'right' }}
                >
                  Status:
                </Typography.Text>
                <UserStatusTag value={user.is_active} />
              </Flex>
            </Flex>
            <Flex wrap vertical gap="10px">
              <Flex gap="10px">
                <Typography.Text
                  strong
                  style={{ width: 70, textAlign: 'right' }}
                >
                  Tier:
                </Typography.Text>
                <UserTierTag value={user.tier} />
              </Flex>
              <Flex gap="10px">
                <Typography.Text
                  strong
                  style={{ width: 70, textAlign: 'right' }}
                >
                  Joined:
                </Typography.Text>
                <Typography.Text>
                  <CalendarOutlined /> {formatDate(user.created_at)}
                </Typography.Text>
              </Flex>
            </Flex>
          </Flex>
        </Col>
      </Row>
    </Card>
  );
};
