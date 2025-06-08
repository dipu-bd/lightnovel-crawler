import { Auth } from '@/store/_auth';
import { Menu } from 'antd';
import { useMemo } from 'react';
import { useSelector } from 'react-redux';
import { useLocation, useNavigate } from 'react-router-dom';
import { buildMenu } from './menu';

export const MainLayoutSidebar: React.FC<{
  onChange: () => any;
}> = ({ onChange }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const isAdmin = useSelector(Auth.select.isAdmin);

  const items = useMemo(() => buildMenu(isAdmin), [isAdmin]);

  const handleMenuClick = (key: string) => {
    if (key && typeof key === 'string' && key.startsWith('/')) {
      navigate(key);
      onChange();
    }
  };

  return (
    <Menu
      mode="inline"
      inlineIndent={15}
      items={items}
      onClick={(info) => handleMenuClick(info.key)}
      selectedKeys={[location.pathname]}
      defaultOpenKeys={[
        'admin', // keep open by default
        ...location.pathname.split('/').filter(Boolean),
      ]}
      style={{
        height: '100%',
      }}
    />
  );
};
