from rest_framework import serializers
from kanmind_app.models import Board, Task, User
from rest_framework.exceptions import PermissionDenied
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


class TaskCreateSerializer(serializers.ModelSerializer):
    assignee_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='assignee', write_only=True, required=False, allow_null=True
    )
    reviewer_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='reviewer', write_only=True, required=False, allow_null=True
    )
    assignee = serializers.SerializerMethodField()
    reviewer = serializers.SerializerMethodField()
    comment_count = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = ['id', 'board', 'title', 'description', 'status', 'priority', 
                  'assignee_id', 'reviewer_id', 'assignee', 'reviewer', 'due_date', 'comment_count']

    def get_assignee(self, obj):
        if obj.assignee:
            return {"id": obj.assignee.id, "email": obj.assignee.email, "fullname": obj.assignee.username}
        return None

    def get_reviewer(self, obj):
        if obj.reviewer:
            return {"id": obj.reviewer.id, "email": obj.reviewer.email, "fullname": obj.reviewer.username}
        return None

    def get_comment_count(self, obj):
        return 0

    def validate(self, attrs):
        request = self.context.get('request')
        board = attrs.get('board')
        
        if request and not (board.owner == request.user or board.members.filter(id=request.user.id).exists()):
            raise PermissionDenied({"detail": "You must be a member of the board to create a task."})
            
        assignee = attrs.get('assignee')
        reviewer = attrs.get('reviewer')
        
        if assignee and not (board.owner == assignee or board.members.filter(id=assignee.id).exists()):
            raise serializers.ValidationError({"assignee_id": "The assignee must be a member of the board."})
            
        if reviewer and not (board.owner == reviewer or board.members.filter(id=reviewer.id).exists()):
            raise serializers.ValidationError({"reviewer_id": "The reviewer must be a member of the board."})

        return attrs


class TaskUpdateSerializer(serializers.ModelSerializer):
    assignee_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='assignee', write_only=True, required=False, allow_null=True
    )
    reviewer_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='reviewer', write_only=True, required=False, allow_null=True
    )
    assignee = serializers.SerializerMethodField()
    reviewer = serializers.SerializerMethodField()
    comment_count = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = ['id', 'board', 'title', 'description', 'status', 'priority', 
                  'assignee_id', 'reviewer_id', 'assignee', 'reviewer', 'due_date', 'comment_count']
        read_only_fields = ['board']

    def get_assignee(self, obj):
        if obj.assignee:
            return {"id": obj.assignee.id, "email": obj.assignee.email, "fullname": obj.assignee.username}
        return None

    def get_reviewer(self, obj):
        if obj.reviewer:
            return {"id": obj.reviewer.id, "email": obj.reviewer.email, "fullname": obj.reviewer.username}
        return None

    def get_comment_count(self, obj):
        return 0

    def validate(self, attrs):
        board = self.instance.board
        assignee = attrs.get('assignee')
        reviewer = attrs.get('reviewer')
        
        if assignee and not (board.owner == assignee or board.members.filter(id=assignee.id).exists()):
            raise serializers.ValidationError({"assignee_id": "The assignee must be a member of the board."})
            
        if reviewer and not (board.owner == reviewer or board.members.filter(id=reviewer.id).exists()):
            raise serializers.ValidationError({"reviewer_id": "The reviewer must be a member of the board."})

        return attrs


class EmailCheckSerializer(serializers.ModelSerializer):

    fullname = serializers.CharField(source='username', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'fullname']
