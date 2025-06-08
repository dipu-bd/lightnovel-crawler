import {
  BookOutlined,
  ControlOutlined,
  DeploymentUnitOutlined,
  FileDoneOutlined,
  TeamOutlined,
} from '@ant-design/icons';
import { type MenuProps } from 'antd';
import { UserInfoCard } from './UserInfo';

export const buildMenu = (isAdmin: boolean): MenuProps['items'] => [
  {
    key: '/me',
    disabled: true,
    style: {
      height: 'fit-content',
    },
    label: <UserInfoCard />,
  },
  {
    type: 'divider',
  },
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
];
