import { UserRole, UserTier } from '@/types';
import { CrownFilled, SmileOutlined, StarFilled } from '@ant-design/icons';
import { Tag } from 'antd';

export const UserTierTag: React.FC<{ value?: UserTier }> = ({ value }) => {
  switch (value) {
    case UserTier.BASIC:
      return <Tag icon={<SmileOutlined />}>Basic</Tag>;
    case UserTier.PREMIUM:
      return (
        <Tag color="gold" icon={<StarFilled />}>
          Premium
        </Tag>
      );
    case UserTier.VIP:
      return (
        <Tag bordered color="volcano-inverse" icon={<CrownFilled />}>
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
    <Tag color={value ? 'green' : 'gray'}>{value ? 'Active' : 'Inactive'}</Tag>
  );
};

export const UserRoleTag: React.FC<{ value?: UserRole }> = ({ value }) => {
  if (!value) return null;
  return (
    <Tag color={value === 'admin' ? 'red' : 'blue'}>{value.toUpperCase()}</Tag>
  );
};
