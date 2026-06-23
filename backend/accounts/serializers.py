from rest_framework import serializers
from .models import Member


class MemberSerializer(serializers.ModelSerializer):
    # 寫入時要 password, 讀取時隱藏
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = Member
        fields = ['id', 'email', 'name', 'phone', 'is_active', 'created_at', 'password']
        read_only_fields = ['id', 'created_at']

    def create(self, validated_data):
        # 用 set_password 做 hash
        member = Member(
            email=validated_data['email'],
            name=validated_data['name'],
            phone=validated_data.get('phone'),
        )
        member.set_password(validated_data['password'])
        member.save()
        return member

    def update(self, instance, validated_data):
        # 若帶 password 才更新
        if 'password' in validated_data:
            instance.set_password(validated_data.pop('password'))
        return super().update(instance, validated_data)
