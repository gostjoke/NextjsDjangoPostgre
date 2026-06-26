'use client';

import { useEffect, useState } from 'react';
import {
  Tabs, Table, Button, Space, Modal, Form,
  Input, Switch, InputNumber, message, Popconfirm,
} from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons';
import { apiFetch, unwrap } from '../../lib/api';

interface Category {
  id: number; name: string; slug: string;
  is_active: boolean; sort_order: number;
}
interface Brand {
  id: number; name: string; logo: string;
  description: string; is_active: boolean;
}

// ---- 通用 CRUD hook ----
function useResource<T extends { id: number }>(endpoint: string) {
  const [list, setList]       = useState<T[]>([]);
  const [loading, setLoading] = useState(true);

  const load = async () => {
    setLoading(true);
    try {
      const data = await apiFetch<unknown>(endpoint);
      setList(unwrap(data as never) as T[]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, []);

  const save = async (values: Partial<T>, id?: number) => {
    if (id) {
      await apiFetch(`${endpoint}${id}/`, { method: 'PATCH', body: JSON.stringify(values) });
    } else {
      await apiFetch(endpoint, { method: 'POST', body: JSON.stringify(values) });
    }
    await load();
  };

  const remove = async (id: number) => {
    await apiFetch(`${endpoint}${id}/`, { method: 'DELETE' });
    await load();
  };

  return { list, loading, save, remove };
}

// ---- 分類 Tab ----
function CategoryTab() {
  const { list, loading, save, remove } = useResource<Category>('/api/store/categories/');
  const [open, setOpen]     = useState(false);
  const [editing, setEditing] = useState<Category | null>(null);
  const [saving, setSaving]   = useState(false);
  const [form] = Form.useForm();

  const openModal = (record?: Category) => {
    setEditing(record ?? null);
    form.setFieldsValue(record ?? { is_active: true, sort_order: 0 });
    setOpen(true);
  };

  const handleSave = async () => {
    const values = await form.validateFields();
    setSaving(true);
    try {
      await save(values, editing?.id);
      message.success(editing ? '更新成功' : '新增成功');
      setOpen(false);
    } catch (e: unknown) {
      message.error((e as Error).message);
    } finally {
      setSaving(false);
    }
  };

  const columns = [
    { title: 'ID',   dataIndex: 'id',         key: 'id',         width: 60 },
    { title: '名稱', dataIndex: 'name',        key: 'name' },
    { title: 'Slug', dataIndex: 'slug',        key: 'slug' },
    { title: '排序', dataIndex: 'sort_order',  key: 'sort_order', width: 70 },
    {
      title: '啟用', dataIndex: 'is_active', key: 'is_active', width: 70,
      render: (v: boolean) => <Switch checked={v} disabled size="small" />,
    },
    {
      title: '操作', key: 'action', width: 130,
      render: (_: unknown, r: Category) => (
        <Space>
          <Button size="small" icon={<EditOutlined />} onClick={() => openModal(r)}>編輯</Button>
          <Popconfirm title="確定刪除？" onConfirm={async () => { await remove(r.id); message.success('刪除成功'); }} okText="刪除" cancelText="取消">
            <Button size="small" danger icon={<DeleteOutlined />}>刪除</Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <>
      <div className="flex justify-end mb-3">
        <Button type="primary" icon={<PlusOutlined />} onClick={() => openModal()}>新增分類</Button>
      </div>
      <Table dataSource={list} columns={columns} rowKey="id" loading={loading} size="middle" pagination={{ pageSize: 10 }} />

      <Modal title={editing ? '編輯分類' : '新增分類'} open={open} onOk={handleSave} onCancel={() => setOpen(false)} confirmLoading={saving} okText="儲存" cancelText="取消">
        <Form form={form} layout="vertical" className="mt-4">
          <Form.Item name="name" label="名稱" rules={[{ required: true }]}><Input /></Form.Item>
          <Form.Item name="slug" label="Slug" rules={[{ required: true }]}><Input /></Form.Item>
          <Form.Item name="sort_order" label="排序"><InputNumber min={0} style={{ width: '100%' }} /></Form.Item>
          <Form.Item name="is_active" label="啟用" valuePropName="checked"><Switch /></Form.Item>
        </Form>
      </Modal>
    </>
  );
}

// ---- 品牌 Tab ----
function BrandTab() {
  const { list, loading, save, remove } = useResource<Brand>('/api/store/brands/');
  const [open, setOpen]     = useState(false);
  const [editing, setEditing] = useState<Brand | null>(null);
  const [saving, setSaving]   = useState(false);
  const [form] = Form.useForm();

  const openModal = (record?: Brand) => {
    setEditing(record ?? null);
    form.setFieldsValue(record ?? { is_active: true });
    setOpen(true);
  };

  const handleSave = async () => {
    const values = await form.validateFields();
    setSaving(true);
    try {
      await save(values, editing?.id);
      message.success(editing ? '更新成功' : '新增成功');
      setOpen(false);
    } catch (e: unknown) {
      message.error((e as Error).message);
    } finally {
      setSaving(false);
    }
  };

  const columns = [
    { title: 'ID',   dataIndex: 'id',        key: 'id',        width: 60 },
    { title: '品牌', dataIndex: 'name',       key: 'name' },
    { title: '描述', dataIndex: 'description', key: 'description', ellipsis: true },
    {
      title: '啟用', dataIndex: 'is_active', key: 'is_active', width: 70,
      render: (v: boolean) => <Switch checked={v} disabled size="small" />,
    },
    {
      title: '操作', key: 'action', width: 130,
      render: (_: unknown, r: Brand) => (
        <Space>
          <Button size="small" icon={<EditOutlined />} onClick={() => openModal(r)}>編輯</Button>
          <Popconfirm title="確定刪除？" onConfirm={async () => { await remove(r.id); message.success('刪除成功'); }} okText="刪除" cancelText="取消">
            <Button size="small" danger icon={<DeleteOutlined />}>刪除</Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <>
      <div className="flex justify-end mb-3">
        <Button type="primary" icon={<PlusOutlined />} onClick={() => openModal()}>新增品牌</Button>
      </div>
      <Table dataSource={list} columns={columns} rowKey="id" loading={loading} size="middle" pagination={{ pageSize: 10 }} />

      <Modal title={editing ? '編輯品牌' : '新增品牌'} open={open} onOk={handleSave} onCancel={() => setOpen(false)} confirmLoading={saving} okText="儲存" cancelText="取消">
        <Form form={form} layout="vertical" className="mt-4">
          <Form.Item name="name" label="品牌名稱" rules={[{ required: true }]}><Input /></Form.Item>
          <Form.Item name="logo" label="Logo URL"><Input placeholder="https://..." /></Form.Item>
          <Form.Item name="description" label="描述"><Input.TextArea rows={2} /></Form.Item>
          <Form.Item name="is_active" label="啟用" valuePropName="checked"><Switch /></Form.Item>
        </Form>
      </Modal>
    </>
  );
}

// ---- 主頁面 ----
export default function CategoriesPage() {
  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold text-gray-800">分類 / 品牌</h1>
      <div className="bg-white rounded-lg p-4">
        <Tabs
          defaultActiveKey="category"
          items={[
            { key: 'category', label: '商品分類', children: <CategoryTab /> },
            { key: 'brand',    label: '品牌管理', children: <BrandTab /> },
          ]}
        />
      </div>
    </div>
  );
}
