from rest_framework import serializers
from kanmind_app.models import Board, Task, User
from django.db.models import F

class BoardListSerializer(serializers.ModelSerializer):
    
    ticket_count = serializers.SerializerMethodField()
    tasks_to_do_count = serializers.SerializerMethodField()
    tasks_high_prio_count = serializers.SerializerMethodField()
    member_count = serializers.SerializerMethodField()

    class Meta:
        model = Board
        fields = ['id', 'title', 'member_count', 'ticket_count', 'tasks_to_do_count', 'tasks_high_prio_count', 'owner']
        read_only_fields = ['owner']

    def get_ticket_count(self, obj):
        return obj.tasks.count()

    def get_tasks_to_do_count(self, obj):
        return obj.tasks.filter(status='to-do').count()

    def get_tasks_high_prio_count(self, obj):
        return obj.tasks.filter(priority='high').count()

    def get_member_count(self,obj):
        return obj.members.count()


class BoardDetailSerializer(serializers.ModelSerializer):

    members = serializers.SerializerMethodField()
    tasks = serializers.SerializerMethodField()

    class Meta:
        model = Board
        fields = ['id', 'title', 'owner', 'members', 'tasks']
        read_only_fields = ['owner']

    def get_members(self, obj):
        return obj.members.values('id', 'email', fullname=F('username'))

    def get_tasks(self, obj):
        return 


class BoardUpdateSerializer(serializers.ModelSerializer):

    owner_data = serializers.SerializerMethodField()
    members_data = serializers.SerializerMethodField()

    members = serializers.PrimaryKeyRelatedField(
        many=True, 
        queryset=User.objects.all(), 
        write_only=True
    )

    class Meta:
        model = Board
        fields = ['id', 'title', 'owner_data', 'members_data', 'members']
        read_only_fields = []

    def get_owner_data(self, obj):
        return {
            "id": obj.owner.id,
            "email": obj.owner.email,
            "fullname": obj.owner.username
        }

    def get_members_data(self, obj):
        return obj.members.values('id', 'email', fullname=F('username'))


class TaskSerializer(serializers.ModelSerializer):

    class Meta:
        model = Task
        fields = ['id', 'board', 'title', 'description', 'status', 'priority', 'assignee', 'reviewer', 'due_date']


class EmailCheckSerializer(serializers.ModelSerializer):

    fullname = serializers.CharField(source='username', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'fullname']
