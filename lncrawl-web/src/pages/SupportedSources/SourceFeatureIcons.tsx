import type { SupportedSource } from '@/types';
import {
  LoginOutlined,
  PictureOutlined,
  SearchOutlined,
  TranslationOutlined,
} from '@ant-design/icons';
import { Tooltip } from 'antd';

const icons = [
  {
    key: 'has_manga',
    icon: <PictureOutlined />,
    label: 'Has Manga',
  },
  {
    key: 'has_mtl',
    icon: <TranslationOutlined />,
    label: 'Has MTL',
  },
  {
    key: 'can_login',
    icon: <LoginOutlined />,
    label: 'Can Login',
  },
  {
    key: 'can_search',
    icon: <SearchOutlined />,
    label: 'Can Search',
  },
  // {
  //   key: 'can_logout',
  //   icon: <LogoutOutlined />,
  //   label: 'Can Logout',
  // },
];

export const SourceFeatureIcons: React.FC<{ source: SupportedSource }> = ({
  source,
}) => (
  <>
    {icons.map(
      ({ key, icon, label }) =>
        (source as any)[key] && (
          <Tooltip key={key} title={label}>
            <span style={{ fontSize: 16 }}>{icon}</span>
          </Tooltip>
        )
    )}
  </>
);
