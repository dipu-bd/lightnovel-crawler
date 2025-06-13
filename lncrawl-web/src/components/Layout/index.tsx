import { Avatar, Divider, Grid, Layout, Typography } from 'antd';
import { useState } from 'react';
import { Outlet, useNavigate } from 'react-router-dom';
import { MainLayoutSidebar } from './sidebar';

export const MainLayout: React.FC<any> = () => {
  const navigate = useNavigate();
  const { md } = Grid.useBreakpoint();
  const [overlay, setOverlay] = useState(false);
  const [collapsed, setCollapsed] = useState(false);

  return (
    <Layout>
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
          top: '0',
        }}
        style={
          overlay
            ? {
                zIndex: 1000,
                top: 0,
                bottom: 0,
                position: 'absolute',
                boxShadow: '0 5px 10px #000',
              }
            : {
                height: '100vh',
              }
        }
      >
        <MainLayoutSidebar onChange={() => setCollapsed(overlay)} />
      </Layout.Sider>
      <Layout.Content
        style={{
          height: '100vh',
          overflow: 'auto',
          padding: md ? 20 : 10,
          paddingBottom: md ? 50 : 100,
        }}
        onClickCapture={() => setCollapsed(overlay)}
      >
        <div
          style={{
            margin: '0 auto',
            maxWidth: 1200,
            minHeight: 'calc(100% - 25px)',
            opacity: overlay && !collapsed ? '0.5' : undefined,
            pointerEvents: overlay && !collapsed ? 'none' : undefined,
            transition: 'all 0.2s ease-in-out',
          }}
        >
          {!md && (
            <>
              <Typography.Title
                level={4}
                style={{ margin: 0, textAlign: 'center' }}
                onClick={() => navigate('/')}
              >
                <Avatar
                  shape="square"
                  src="/lncrawl.svg"
                  size={28}
                  style={{ marginBottom: 5 }}
                />
                Lightnovel Crawler
              </Typography.Title>
              <Divider size="small" />
            </>
          )}
          <Outlet />
        </div>
      </Layout.Content>
    </Layout>
  );
};
