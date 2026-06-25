'use client';

import { Badge, Button, Input } from 'antd';
import {
  ShoppingCartOutlined,
  UserOutlined,
  SearchOutlined,
} from '@ant-design/icons';
import Link from 'next/link';

export default function Navbar() {
  return (
    <header className="sticky top-0 z-50 bg-white shadow-sm">
      <div className="max-w-7xl mx-auto px-4 h-16 flex items-center gap-6">
        {/* Logo */}
        <Link href="/" className="text-xl font-bold text-gray-900 shrink-0">
          ShopNow
        </Link>

        {/* 搜尋框 */}
        <Input
          placeholder="搜尋商品..."
          prefix={<SearchOutlined className="text-gray-400" />}
          className="flex-1 max-w-xl"
          size="large"
        />

        {/* 右側操作 */}
        <div className="flex items-center gap-3 ml-auto shrink-0">
          <Button icon={<UserOutlined />} type="text" size="large">
            登入
          </Button>
          <Badge count={0} showZero={false}>
            <Button icon={<ShoppingCartOutlined />} type="text" size="large" />
          </Badge>
        </div>
      </div>
    </header>
  );
}
