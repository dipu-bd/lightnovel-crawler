import type { User } from '@/types';
import {
  BookOutlined,
  ControlOutlined,
  DeploymentUnitOutlined,
  FileDoneOutlined,
  LogoutOutlined,
  TeamOutlined,
} from '@ant-design/icons';
import { Button, Flex, Typography, type MenuProps } from 'antd';
import { UserAvatar } from '../Tags/gravatar';

export const buildMenu = ({
  isAdmin,
  authUser,
  handleLogout,
}: {
  isAdmin: boolean;
  authUser: User | null;
  handleLogout: () => void;
}): MenuProps['items'] => [
  {
    key: '/me',
    style: {
      height: 'fit-content',
    },
    label: (
      <Flex
        vertical
        gap="5px"
        align="center"
        justify="center"
        style={{
          paddingTop: '18px',
          textAlign: 'center',
        }}
      >
        <UserAvatar
          size={72}
          user={authUser}
          style={{ backgroundColor: 'blueviolet' }}
        />
        <Typography.Text strong>{authUser?.name}</Typography.Text>
      </Flex>
    ),
  },
  {
    disabled: true,
    key: 'logout',
    style: {
      height: '50px',
    },
    label: (
      <Button
        block
        type="default"
        onClick={handleLogout}
        icon={<LogoutOutlined />}
        children="Logout"
      />
    ),
  },
  {
    type: 'divider',
  },
  {
    type: 'group',
    style: {
      height: 'calc(100vh - 210px)',
      overflow: 'auto',
    },
    children: [
      {
        key: '/',
        label: 'Novels',
        icon: <BookOutlined />,
      },
      {
        key: '/jobs',
        label: 'Jobs',
        icon: <DeploymentUnitOutlined />,
      },
      {
        type: 'divider',
      },
      {
        key: '/meta/sources',
        label: 'Supported Sources',
        icon: <FileDoneOutlined />,
      },
      {
        type: 'divider',
        style: { display: isAdmin ? undefined : 'none' },
      },
      {
        key: 'admin',
        label: 'Administration',
        icon: <ControlOutlined />,
        style: { display: isAdmin ? undefined : 'none' },
        children: [
          {
            key: '/admin/users',
            label: 'Users',
            icon: <TeamOutlined />,
          },
        ],
      },
    ],
  },
];
