'use client';

import { useEffect, useState } from 'react';
import { Card, Col, Row, Statistic, Table, Tag, Spin } from 'antd';
import {
  ShoppingOutlined,
  OrderedListOutlined,
  TagsOutlined,
  DollarOutlined,
} from '@ant-design/icons';
import { apiFetch, unwrap } from '../lib/api';

interface Order {
  id: number;
  order_no: string;
  status: string;
  total_amount: string;
  created_at: string;
}

// 訂單狀態 Tag 對應
const statusColor: Record<string, string> = {
  pending: 'orange', paid: 'blue', shipped: 'cyan',
  delivered: 'geekblue', completed: 'green',
  cancelled: 'red', refunded: 'volcano',
};
const statusLabel: Record<string, string> = {
  pending: '待付款', paid: '已付款', shipped: '已出貨',
  delivered: '已送達', completed: '已完成',
  cancelled: '已取消', refunded: '已退款',
};

const recentOrderCols = [
  { title: '訂單編號', dataIndex: 'order_no', key: 'order_no' },
  {
    title: '狀態', dataIndex: 'status', key: 'status',
    render: (s: string) => <Tag color={statusColor[s]}>{statusLabel[s] ?? s}</Tag>,
  },
  {
    title: '金額', dataIndex: 'total_amount', key: 'total_amount',
    render: (v: string) => `NT$ ${parseFloat(v).toLocaleString('zh-TW')}`,
  },
  {
    title: '時間', dataIndex: 'created_at', key: 'created_at',
    render: (v: string) => new Date(v).toLocaleDateString('zh-TW'),
  },
];

export default function DashboardPage() {
  const [stats, setStats] = useState({ products: 0, orders: 0, categories: 0, revenue: 0 });
  const [recentOrders, setRecentOrders] = useState<Order[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.allSettled([
      apiFetch<unknown>('/api/store/products/'),
      apiFetch<unknown>('/api/store/orders/'),
      apiFetch<unknown>('/api/store/categories/'),
    ]).then(([products, orders, categories]) => {
      const productList = products.status === 'fulfilled' ? unwrap(products.value as never) : [];
      const orderList   = orders.status   === 'fulfilled' ? unwrap(orders.value   as never) as Order[] : [];
      const categoryList = categories.status === 'fulfilled' ? unwrap(categories.value as never) : [];

      // 計算總營收 (completed 訂單)
      const revenue = orderList
        .filter((o) => o.status === 'completed')
        .reduce((sum, o) => sum + parseFloat(o.total_amount), 0);

      setStats({
        products: productList.length,
        orders: orderList.length,
        categories: categoryList.length,
        revenue,
      });
      // 最近 5 筆訂單
      setRecentOrders(orderList.slice(0, 5));
    }).finally(() => setLoading(false));
  }, []);

  if (loading) {
    return <div className="flex justify-center py-32"><Spin size="large" /></div>;
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-800">總覽</h1>

      {/* 統計卡片 */}
      <Row gutter={[16, 16]}>
        {[
          { title: '商品總數', value: stats.products, icon: <ShoppingOutlined />, color: '#1677ff' },
          { title: '訂單總數', value: stats.orders,   icon: <OrderedListOutlined />, color: '#52c41a' },
          { title: '商品分類', value: stats.categories, icon: <TagsOutlined />,    color: '#faad14' },
          {
            title: '累計營收', value: stats.revenue, icon: <DollarOutlined />, color: '#f5222d',
            prefix: 'NT$ ', formatter: (v: number) => v.toLocaleString('zh-TW'),
          },
        ].map((card) => (
          <Col xs={24} sm={12} xl={6} key={card.title}>
            <Card>
              <Statistic
                title={card.title}
                value={card.value}
                prefix={
                  <span style={{ color: card.color, marginRight: 8 }}>{card.icon}</span>
                }
                valueStyle={{ color: card.color }}
                formatter={card.formatter ? (v) => `NT$ ${card.formatter!(v as number)}` : undefined}
              />
            </Card>
          </Col>
        ))}
      </Row>

      {/* 最近訂單 */}
      <Card title="最近訂單" className="mt-4">
        <Table
          dataSource={recentOrders}
          columns={recentOrderCols}
          rowKey="id"
          pagination={false}
          size="small"
          locale={{ emptyText: '尚無訂單' }}
        />
      </Card>
    </div>
  );
}
