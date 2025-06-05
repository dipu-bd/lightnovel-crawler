import { store } from '@/store';
import { Auth } from '@/store/_auth';
import { Menu } from 'antd';
import { useMemo } from 'react';
import { useSelector } from 'react-redux';
import { useLocation } from 'react-router-dom';
import { buildMenu } from './menu';

export const MainLayoutSidebar: React.FC<any> = () => {
  const location = useLocation();
  const authUser = useSelector(Auth.select.user);
  const isAdmin = useSelector(Auth.select.isAdmin);

  const items = useMemo(() => {
    return buildMenu({
      isAdmin,
      authUser,
      handleLogout: () => {
        store.dispatch(Auth.action.clearAuth());
      },
    });
  }, [isAdmin, authUser]);

  return (
    <Menu
      mode="inline"
      inlineIndent={15}
      items={items}
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
