"""
mq app serializers
注意: 目前 mq 沒有自己的 model, 此檔保留給之後擴充用
若 views.py 引用了 EHSMainTableSerializer 卻沒有對應 model,
請改成自己專案實際存在的 model
"""
from rest_framework import serializers


# 範例: 通用訊息 serializer (publish API 用)
class PublishMessageSerializer(serializers.Serializer):
    queue = serializers.CharField(max_length=255)
    payload = serializers.DictField(required=False, default=dict)
