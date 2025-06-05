import { Layout } from 'antd';
import { useState } from 'react';
import { Outlet } from 'react-router-dom';
import { MainLayoutSidebar } from './sidebar';

export default function MainLayout() {
  const [overlay, setOverlay] = useState(false);
  const [collapsed, setCollapsed] = useState(false);

  return (
    <Layout style={{ minWidth: '350px', overflow: 'auto' }}>
      <Layout.Sider
        theme="light"
        breakpoint="md"
        collapsedWidth={0}
        width={250}
        collapsed={collapsed}
        onCollapse={(collapsed, type) => {
          setCollapsed(collapsed);
          if (type === 'responsive') {
            setOverlay(collapsed);
          }
        }}
        zeroWidthTriggerStyle={{
          top: '10px',
        }}
        style={
          overlay
            ? {
                zIndex: 1000,
                position: 'absolute',
                boxShadow: '0 5px 10px #000',
              }
            : undefined
        }
      >
        <MainLayoutSidebar />
      </Layout.Sider>
      <Layout.Content
        style={{ height: '100vh', overflow: 'auto' }}
        onClickCapture={() => setCollapsed(overlay)}
      >
        <Outlet />
      </Layout.Content>
    </Layout>
  );
}
