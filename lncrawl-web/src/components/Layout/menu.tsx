import type { AuthUser } from '@/types';
import {
  BookOutlined,
  ControlOutlined,
  DeploymentUnitOutlined,
  ExperimentOutlined,
  LogoutOutlined,
  UserOutlined,
} from '@ant-design/icons';
import { Button, Flex, Typography, type MenuProps } from 'antd';
import { Link } from 'react-router-dom';

export function buildMenu({
  isAdmin,
  authUser,
  handleLogout,
}: {
  isAdmin: boolean;
  authUser: AuthUser | null;
  handleLogout: () => void;
}): MenuProps['items'] {
  const items: MenuProps['items'] = [
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
          <UserOutlined style={{ fontSize: '64px', paddingLeft: '5px' }} />
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
          label: 'Home',
          icon: <ExperimentOutlined />,
        },
        {
          key: '/novels',
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
          style: { display: isAdmin ? undefined : 'none' },
        },
        {
          key: 'admin',
          label: 'Administration',
          icon: <ControlOutlined />,
          style: { display: isAdmin ? undefined : 'none' },
          children: [
            {
              key: '/users',
              label: 'Users',
              icon: <UserOutlined />,
            },
          ],
        },
      ],
    },
  ];

  return linkify(items);
}

function linkify(items: any): any {
  if (!items) return;
  for (const item of items) {
    if (item.children) {
      linkify(item.children);
    }
    if (item.disabled) continue;
    if (item.key?.startsWith('/') && typeof item.label === 'string') {
      item.label = (
        <Link to={item.key} style={{ color: 'inherit' }}>
          {item.label}
        </Link>
      );
    }
  }
  return items;
}
