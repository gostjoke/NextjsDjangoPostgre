'use client';

import { useEffect, useState } from 'react';
import {
  Button, Table, Tag, Space, Modal, Form,
  Input, InputNumber, Select, message, Popconfirm,
} from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons';
import { apiFetch, unwrap } from '../../lib/api';

interface Category { id: number; name: string }
interface Brand    { id: number; name: string }
interface Product {
  id: number; name: string; slug: string; status: string;
  base_price: string; sales_count: number;
  category: number; brand: number | null;
}

const STATUS_OPTIONS = [
  { value: 'draft',    label: '草稿' },
  { value: 'on_sale',  label: '上架' },
  { value: 'off_sale', label: '下架' },
  { value: 'sold_out', label: '售完' },
];
const statusColor: Record<string, string> = {
  draft: 'default', on_sale: 'green', off_sale: 'orange', sold_out: 'red',
};
const statusLabel: Record<string, string> = {
  draft: '草稿', on_sale: '上架中', off_sale: '已下架', sold_out: '已售完',
};

export default function ProductsPage() {
  const [products,   setProducts]   = useState<Product[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [brands,     setBrands]     = useState<Brand[]>([]);
  const [loading,    setLoading]    = useState(true);
  const [modalOpen,  setModalOpen]  = useState(false);
  const [editing,    setEditing]    = useState<Product | null>(null);
  const [saving,     setSaving]     = useState(false);
  const [form] = Form.useForm();

  // 載入商品、分類、品牌
  const load = async () => {
    setLoading(true);
    try {
      const [p, c, b] = await Promise.all([
        apiFetch<unknown>('/api/store/products/'),
        apiFetch<unknown>('/api/store/categories/'),
        apiFetch<unknown>('/api/store/brands/'),
      ]);
      setProducts(unwrap(p as never) as Product[]);
      setCategories(unwrap(c as never) as Category[]);
      setBrands(unwrap(b as never) as Brand[]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, []);

  // 開啟新增 / 編輯 Modal
  const openModal = (record?: Product) => {
    setEditing(record ?? null);
    form.setFieldsValue(
      record
        ? { ...record, base_price: parseFloat(record.base_price) }
        : { status: 'draft' },
    );
    setModalOpen(true);
  };

  // 送出表單
  const handleSave = async () => {
    const values = await form.validateFields();
    setSaving(true);
    try {
      if (editing) {
        await apiFetch(`/api/store/products/${editing.id}/`, {
          method: 'PATCH', body: JSON.stringify(values),
        });
        message.success('更新成功');
      } else {
        await apiFetch('/api/store/products/', {
          method: 'POST', body: JSON.stringify(values),
        });
        message.success('新增成功');
      }
      setModalOpen(false);
      load();
    } catch (e: unknown) {
      message.error((e as Error).message);
    } finally {
      setSaving(false);
    }
  };

  // 刪除
  const handleDelete = async (id: number) => {
    try {
      await apiFetch(`/api/store/products/${id}/`, { method: 'DELETE' });
      message.success('刪除成功');
      load();
    } catch (e: unknown) {
      message.error((e as Error).message);
    }
  };

  const columns = [
    { title: 'ID',   dataIndex: 'id',   key: 'id',   width: 60 },
    { title: '商品名稱', dataIndex: 'name', key: 'name' },
    {
      title: '狀態', dataIndex: 'status', key: 'status', width: 90,
      render: (s: string) => <Tag color={statusColor[s]}>{statusLabel[s]}</Tag>,
    },
    {
      title: '售價', dataIndex: 'base_price', key: 'base_price', width: 110,
      render: (v: string) => `NT$ ${parseFloat(v).toLocaleString('zh-TW')}`,
    },
    { title: '銷售量', dataIndex: 'sales_count', key: 'sales_count', width: 80 },
    {
      title: '操作', key: 'action', width: 120,
      render: (_: unknown, record: Product) => (
        <Space>
          <Button size="small" icon={<EditOutlined />} onClick={() => openModal(record)}>編輯</Button>
          <Popconfirm title="確定刪除？" onConfirm={() => handleDelete(record.id)} okText="刪除" cancelText="取消">
            <Button size="small" danger icon={<DeleteOutlined />}>刪除</Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-800">商品管理</h1>
        <Button type="primary" icon={<PlusOutlined />} onClick={() => openModal()}>新增商品</Button>
      </div>

      <Table
        dataSource={products}
        columns={columns}
        rowKey="id"
        loading={loading}
        pagination={{ pageSize: 10, showSizeChanger: false }}
        size="middle"
      />

      {/* 新增 / 編輯 Modal */}
      <Modal
        title={editing ? '編輯商品' : '新增商品'}
        open={modalOpen}
        onOk={handleSave}
        onCancel={() => setModalOpen(false)}
        confirmLoading={saving}
        okText="儲存"
        cancelText="取消"
        width={560}
      >
        <Form form={form} layout="vertical" className="mt-4">
          <Form.Item name="name" label="商品名稱" rules={[{ required: true }]}>
            <Input placeholder="請輸入商品名稱" />
          </Form.Item>
          <Form.Item name="slug" label="Slug" rules={[{ required: true }]}>
            <Input placeholder="e.g. my-product" />
          </Form.Item>
          <Form.Item name="base_price" label="售價 (NT$)" rules={[{ required: true }]}>
            <InputNumber min={0} step={1} style={{ width: '100%' }} />
          </Form.Item>
          <Form.Item name="category" label="分類" rules={[{ required: true }]}>
            <Select options={categories.map((c) => ({ value: c.id, label: c.name }))} />
          </Form.Item>
          <Form.Item name="brand" label="品牌">
            <Select allowClear options={brands.map((b) => ({ value: b.id, label: b.name }))} />
          </Form.Item>
          <Form.Item name="status" label="狀態" rules={[{ required: true }]}>
            <Select options={STATUS_OPTIONS} />
          </Form.Item>
          <Form.Item name="description" label="描述">
            <Input.TextArea rows={3} />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
}
