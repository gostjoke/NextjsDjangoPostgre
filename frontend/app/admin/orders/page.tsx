'use client';

import { useEffect, useState } from 'react';
import {
  Table, Tag, Select, Button, Modal, Descriptions, Divider, message,
} from 'antd';
import { EyeOutlined } from '@ant-design/icons';
import { apiFetch, unwrap } from '../../lib/api';

interface OrderItem {
  id: number; product_name: string; sku: string;
  quantity: number; unit_price: string; subtotal: string;
}
interface Order {
  id: number; order_no: string; status: string;
  total_amount: string; subtotal: string; shipping_fee: string;
  recipient_name: string; recipient_phone: string;
  shipping_address: string; note: string;
  created_at: string; items: OrderItem[];
}

const STATUS_OPTIONS = [
  { value: '',          label: '全部' },
  { value: 'pending',   label: '待付款' },
  { value: 'paid',      label: '已付款' },
  { value: 'shipped',   label: '已出貨' },
  { value: 'delivered', label: '已送達' },
  { value: 'completed', label: '已完成' },
  { value: 'cancelled', label: '已取消' },
  { value: 'refunded',  label: '已退款' },
];
const statusColor: Record<string, string> = {
  pending: 'orange', paid: 'blue', shipped: 'cyan',
  delivered: 'geekblue', completed: 'green',
  cancelled: 'red', refunded: 'volcano',
};

export default function OrdersPage() {
  const [orders,      setOrders]      = useState<Order[]>([]);
  const [filtered,    setFiltered]    = useState<Order[]>([]);
  const [loading,     setLoading]     = useState(true);
  const [statusFilter, setStatusFilter] = useState('');
  const [detail,      setDetail]      = useState<Order | null>(null);

  const load = async () => {
    setLoading(true);
    try {
      const data = await apiFetch<unknown>('/api/store/orders/');
      const list = unwrap(data as never) as Order[];
      setOrders(list);
      setFiltered(list);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, []);

  // 前端過濾狀態
  useEffect(() => {
    setFiltered(statusFilter ? orders.filter((o) => o.status === statusFilter) : orders);
  }, [statusFilter, orders]);

  // 更新訂單狀態
  const updateStatus = async (order: Order, newStatus: string) => {
    try {
      await apiFetch(`/api/store/orders/${order.id}/`, {
        method: 'PATCH', body: JSON.stringify({ status: newStatus }),
      });
      message.success('狀態已更新');
      load();
      setDetail(null);
    } catch (e: unknown) {
      message.error((e as Error).message);
    }
  };

  const columns = [
    { title: '訂單編號', dataIndex: 'order_no', key: 'order_no', width: 200 },
    {
      title: '狀態', dataIndex: 'status', key: 'status', width: 100,
      render: (s: string) => (
        <Tag color={statusColor[s]}>
          {STATUS_OPTIONS.find((o) => o.value === s)?.label ?? s}
        </Tag>
      ),
    },
    {
      title: '金額', dataIndex: 'total_amount', key: 'total_amount', width: 130,
      render: (v: string) => `NT$ ${parseFloat(v).toLocaleString('zh-TW')}`,
    },
    { title: '收件人', dataIndex: 'recipient_name', key: 'recipient_name', width: 100 },
    {
      title: '下單時間', dataIndex: 'created_at', key: 'created_at', width: 140,
      render: (v: string) => new Date(v).toLocaleString('zh-TW'),
    },
    {
      title: '操作', key: 'action', width: 80,
      render: (_: unknown, r: Order) => (
        <Button size="small" icon={<EyeOutlined />} onClick={() => setDetail(r)}>查看</Button>
      ),
    },
  ];

  const itemColumns = [
    { title: '商品', dataIndex: 'product_name', key: 'product_name' },
    { title: 'SKU',  dataIndex: 'sku',           key: 'sku' },
    { title: '數量', dataIndex: 'quantity',       key: 'quantity', width: 70 },
    {
      title: '單價', dataIndex: 'unit_price', key: 'unit_price', width: 110,
      render: (v: string) => `NT$ ${parseFloat(v).toLocaleString('zh-TW')}`,
    },
    {
      title: '小計', dataIndex: 'subtotal', key: 'subtotal', width: 110,
      render: (v: string) => `NT$ ${parseFloat(v).toLocaleString('zh-TW')}`,
    },
  ];

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-800">訂單管理</h1>
        {/* 狀態篩選 */}
        <Select
          value={statusFilter}
          onChange={setStatusFilter}
          options={STATUS_OPTIONS}
          style={{ width: 130 }}
          placeholder="篩選狀態"
        />
      </div>

      <Table
        dataSource={filtered}
        columns={columns}
        rowKey="id"
        loading={loading}
        size="middle"
        pagination={{ pageSize: 15, showSizeChanger: false }}
      />

      {/* 訂單詳情 Modal */}
      <Modal
        title={`訂單詳情 — ${detail?.order_no}`}
        open={!!detail}
        onCancel={() => setDetail(null)}
        width={680}
        footer={[
          <Button key="close" onClick={() => setDetail(null)}>關閉</Button>,
          // 快速推進狀態
          detail?.status === 'paid' && (
            <Button key="ship" type="primary" onClick={() => updateStatus(detail, 'shipped')}>
              標記已出貨
            </Button>
          ),
          detail?.status === 'shipped' && (
            <Button key="deliver" type="primary" onClick={() => updateStatus(detail, 'delivered')}>
              標記已送達
            </Button>
          ),
          detail?.status === 'delivered' && (
            <Button key="complete" type="primary" onClick={() => updateStatus(detail, 'completed')}>
              標記已完成
            </Button>
          ),
        ].filter(Boolean)}
      >
        {detail && (
          <>
            <Descriptions size="small" column={2} bordered>
              <Descriptions.Item label="狀態">
                <Tag color={statusColor[detail.status]}>
                  {STATUS_OPTIONS.find((o) => o.value === detail.status)?.label}
                </Tag>
              </Descriptions.Item>
              <Descriptions.Item label="下單時間">
                {new Date(detail.created_at).toLocaleString('zh-TW')}
              </Descriptions.Item>
              <Descriptions.Item label="收件人">{detail.recipient_name}</Descriptions.Item>
              <Descriptions.Item label="電話">{detail.recipient_phone}</Descriptions.Item>
              <Descriptions.Item label="地址" span={2}>{detail.shipping_address}</Descriptions.Item>
              {detail.note && <Descriptions.Item label="備註" span={2}>{detail.note}</Descriptions.Item>}
            </Descriptions>

            <Divider orientation="left" plain>品項</Divider>
            <Table
              dataSource={detail.items}
              columns={itemColumns}
              rowKey="id"
              size="small"
              pagination={false}
              summary={() => (
                <Table.Summary.Row>
                  <Table.Summary.Cell index={0} colSpan={4} align="right">
                    <strong>總計</strong>
                  </Table.Summary.Cell>
                  <Table.Summary.Cell index={1}>
                    <strong>NT$ {parseFloat(detail.total_amount).toLocaleString('zh-TW')}</strong>
                  </Table.Summary.Cell>
                </Table.Summary.Row>
              )}
            />
          </>
        )}
      </Modal>
    </div>
  );
}
