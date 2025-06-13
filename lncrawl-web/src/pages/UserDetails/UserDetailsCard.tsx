import { type User } from '@/types';
import { Card, Flex, Space, Typography } from 'antd';

import { UserAvatar } from '@/components/Tags/gravatar';
import {
  UserRoleTag,
  UserStatusTag,
  UserTierTag,
} from '@/components/Tags/users';
import { formatDate } from '@/utils/time';
import { CalendarOutlined } from '@ant-design/icons';
import { Col, Row } from 'antd';

const { Text, Title } = Typography;

export const UserDetailsCard: React.FC<{ user: User }> = ({ user }) => {
  return (
    <Card variant="outlined">
      <Title level={4} style={{ margin: 0, marginBottom: 16 }}>
        Initiated By
      </Title>

      <Row align="middle" gutter={[16, 16]}>
        <Col flex="auto">
          <Space size="middle">
            <UserAvatar
              size={56}
              user={user}
              style={{ backgroundColor: '#1890ff' }}
            />
            <Flex vertical>
              <Title level={5} style={{ margin: 0 }}>
                {user.name || 'Unknown User'}
              </Title>
              {/* <Text type="secondary">{user.email}</Text> */}
            </Flex>
          </Space>
        </Col>

        <Col flex="auto">
          <Flex wrap gap="10px" justify="space-between">
            <Flex wrap vertical gap="10px">
              <Flex gap="10px">
                <Text strong style={{ width: 70, textAlign: 'right' }}>
                  Role:
                </Text>
                <UserRoleTag value={user.role} />
              </Flex>
              <Flex gap="10px">
                <Text strong style={{ width: 70, textAlign: 'right' }}>
                  Status:
                </Text>
                <UserStatusTag value={user.is_active} />
              </Flex>
            </Flex>
            <Flex wrap vertical gap="10px">
              <Flex gap="10px">
                <Text strong style={{ width: 70, textAlign: 'right' }}>
                  Tier:
                </Text>
                <UserTierTag value={user.tier} />
              </Flex>
              <Flex gap="10px">
                <Text strong style={{ width: 70, textAlign: 'right' }}>
                  Joined:
                </Text>
                <Text>
                  <CalendarOutlined /> {formatDate(user.created_at)}
                </Text>
              </Flex>
            </Flex>
          </Flex>
        </Col>
      </Row>
    </Card>
  );
};
