import type { User } from '@/types';
import { UserOutlined } from '@ant-design/icons';
import { Avatar, type AvatarProps } from 'antd';
import md5 from 'spark-md5';

const getGravatarUrl = (email: string, size = 200) => {
  const hash = md5.hash(email.trim().toLowerCase());
  return `https://www.gravatar.com/avatar/${hash}?d=identicon&s=${size}`;
};

export const UserAvatar: React.FC<
  {
    user?: User | null;
  } & AvatarProps
> = ({ user, ...avatarProps }) => {
  if (!user) return null;

  return (
    <Avatar
      size={72}
      {...avatarProps}
      alt={user.name || user.email}
      src={getGravatarUrl(user.email)}
      icon={<UserOutlined style={{ fontSize: 'inherit' }} />}
    />
  );
};
