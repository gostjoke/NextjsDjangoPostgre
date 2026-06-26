'use client';

import { useState } from 'react';
import { Layout, Menu, Button, Avatar, Dropdown, theme } from 'antd';
import {
  DashboardOutlined,
  ShoppingOutlined,
  TagsOutlined,
  OrderedListOutlined,
  LogoutOutlined,
  UserOutlined,
  MenuFoldOutlined,
  MenuUnfoldOutlined,
} from '@ant-design/icons';
import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';

const { Sider, Header, Content } = Layout;

const menuItems = [
  { key: '/admin',            icon: <DashboardOutlined />, label: <Link href="/admin">總覽</Link> },
  { key: '/admin/products',   icon: <ShoppingOutlined />,  label: <Link href="/admin/products">商品管理</Link> },
  { key: '/admin/categories', icon: <TagsOutlined />,      label: <Link href="/admin/categories">分類 / 品牌</Link> },
  { key: '/admin/orders',     icon: <OrderedListOutlined />, label: <Link href="/admin/orders">訂單管理</Link> },
];

export default function AdminLayout({ children }: { children: React.ReactNode }) {
  const [collapsed, setCollapsed] = useState(false);
  const pathname = usePathname();
  const router = useRouter();
  const { token } = theme.useToken();

  // 登出: 清 token 並跳回首頁
  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    router.push('/');
  };

  const userMenu = {
    items: [
      { key: 'logout', icon: <LogoutOutlined />, label: '登出', danger: true },
    ],
    onClick: ({ key }: { key: string }) => {
      if (key === 'logout') handleLogout();
    },
  };

  return (
    <Layout style={{ minHeight: '100vh' }}>
      {/* ===== 側邊欄 ===== */}
      <Sider
        collapsible
        collapsed={collapsed}
        trigger={null}
        width={220}
        style={{ background: token.colorBgContainer, borderRight: `1px solid ${token.colorBorderSecondary}` }}
      >
        {/* Logo 區 */}
        <div className="flex items-center gap-2 px-5 h-16 border-b border-gray-100">
          <span className="text-lg font-bold text-gray-900 whitespace-nowrap">
            {collapsed ? 'SN' : 'ShopNow 後台'}
          </span>
        </div>

        <Menu
          mode="inline"
          selectedKeys={[pathname]}
          items={menuItems}
          style={{ border: 'none', marginTop: 8 }}
        />
      </Sider>

      <Layout>
        {/* ===== 頂部 Header ===== */}
        <Header
          style={{
            background: token.colorBgContainer,
            borderBottom: `1px solid ${token.colorBorderSecondary}`,
            padding: '0 24px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
          }}
        >
          {/* 收合按鈕 */}
          <Button
            type="text"
            icon={collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
            onClick={() => setCollapsed(!collapsed)}
            size="large"
          />

          {/* 右側使用者 */}
          <Dropdown menu={userMenu} placement="bottomRight">
            <div className="flex items-center gap-2 cursor-pointer">
              <Avatar icon={<UserOutlined />} />
              {!collapsed && <span className="text-sm">管理員</span>}
            </div>
          </Dropdown>
        </Header>

        {/* ===== 主內容 ===== */}
        <Content style={{ margin: 24, background: token.colorBgLayout }}>
          {children}
        </Content>
      </Layout>
    </Layout>
  );
}
