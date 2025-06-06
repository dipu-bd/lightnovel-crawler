import { UserRole, UserTier } from '@/types';
import { CrownFilled, SmileOutlined, StarFilled } from '@ant-design/icons';
import { Tag } from 'antd';

export const UserTierTag: React.FC<{ value?: UserTier }> = ({ value }) => {
  switch (value) {
    case UserTier.BASIC:
      return (
        <Tag icon={<SmileOutlined />} style={{ margin: 0 }}>
          Basic
        </Tag>
      );
    case UserTier.PREMIUM:
      return (
        <Tag color="gold" icon={<StarFilled />} style={{ margin: 0 }}>
          Premium
        </Tag>
      );
    case UserTier.VIP:
      return (
        <Tag
          bordered
          color="volcano-inverse"
          icon={<CrownFilled />}
          style={{ margin: 0 }}
        >
          VIP
        </Tag>
      );
    default:
      return null;
  }
};

export const UserStatusTag: React.FC<{ value?: boolean }> = ({ value }) => {
  if (!value) return null;
  return (
    <Tag color={value ? 'green' : 'gray'} style={{ margin: 0 }}>
      {value ? 'Active' : 'Inactive'}
    </Tag>
  );
};

export const UserRoleTag: React.FC<{ value?: UserRole }> = ({ value }) => {
  if (!value) return null;
  return (
    <Tag color={value === 'admin' ? 'red' : 'blue'} style={{ margin: 0 }}>
      {value.toUpperCase()}
    </Tag>
  );
};
