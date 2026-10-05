from rest_framework import serializers
from ..models import User, Board

class RegisterSerializer(serializers.ModelSerializer):

    repeated_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'repeated_password']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate(self, data):
        if data['password'] != data['repeated_password']:
            raise serializers.ValidationError({'repeated_password': 'Passwords do not match.'})
        return data

    def create(self, validated_data):
        validated_data.pop('repeated_password')

        user = User.objects.create_user(**validated_data)
        return user

class BoardSerializer(serializers.ModelSerializer):

    ticket_count = serializers.SerializerMethodField()
    tasks_to_do_count = serializers.SerializerMethodField()
    tasks_high_prio_count = serializers.SerializerMethodField()

    class Meta:
        model = Board
        fields = ['id', 'title', 'members', 'ticket_count', 'tasks_to_do_count', 'tasks_high_prio_count', 'owner']
        read_only_fields = ['owner']

    def get_ticket_count(self, obj):
        return obj.tasks.count()

    def get_tasks_to_do_count(self, obj):
        return obj.tasks.filter(status='to-do').count()

    def get_tasks_high_prio_count(self, obj):
        return obj.tasks.filter(priority='high').count()