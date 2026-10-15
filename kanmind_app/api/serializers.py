from rest_framework import serializers
from kanmind_app.models import Board, Task, User, Comment
from rest_framework.exceptions import PermissionDenied
from django.db.models import F, Count

class BoardListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing and creating boards without N+1 queries.
    """
    member_count = serializers.IntegerField(read_only=True)
    ticket_count = serializers.IntegerField(read_only=True)
    tasks_to_do_count = serializers.IntegerField(read_only=True)
    tasks_high_prio_count = serializers.IntegerField(read_only=True)

    owner_id = serializers.ReadOnlyField(source='owner.id') 

    members = serializers.PrimaryKeyRelatedField(
        many=True, 
        queryset=User.objects.all(), 
        write_only=True,
        required=False
    )

    class Meta:
        model = Board
        fields = [
            'id', 'title', 'member_count', 'ticket_count', 
            'tasks_to_do_count', 'tasks_high_prio_count', 
            'owner_id', 'members'
        ]


class BoardDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for retrieving detailed board information including tasks and members.
    """
    members = serializers.SerializerMethodField()
    tasks = serializers.SerializerMethodField()

    class Meta:
        model = Board
        fields = ['id', 'title', 'owner', 'members', 'tasks']
        read_only_fields = ['owner']

    def get_members(self, obj):
        """
        Returns board members formatted with id, email, and fullname.
        """
        return obj.members.values('id', 'email', fullname=F('username'))

    def get_tasks(self, obj):
        """
        Returns all tasks associated with this board using the TaskUpdateSerializer.
        """
        tasks = obj.tasks.select_related('assignee', 'reviewer').annotate(
            comment_count=Count('comments', distinct=True)
        )
        return TaskUpdateSerializer(tasks, many=True).data


class BoardUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating board details and managing board memberships.
    """
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
        """
        Formats the owner data for the response output.
        """
        return {
            "id": obj.owner.id,
            "email": obj.owner.email,
            "fullname": obj.owner.username
        }

    def get_members_data(self, obj):
        """
        Formats the updated members list for the response output.
        """
        return obj.members.values('id', 'email', fullname=F('username'))


class TaskCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a new task.
    """
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
        """
        Returns the assignee as a formatted dictionary.
        """
        if obj.assignee:
            return {"id": obj.assignee.id, "email": obj.assignee.email, "fullname": obj.assignee.username}
        return None

    def get_reviewer(self, obj):
        """
        Returns the reviewer as a formatted dictionary.
        """
        if obj.reviewer:
            return {"id": obj.reviewer.id, "email": obj.reviewer.email, "fullname": obj.reviewer.username}
        return None

    def get_comment_count(self, obj):
        """
        Returns the total number of comments associated with the task.
        """
        return getattr(obj, 'comment_count', obj.comments.count())

    def validate(self, attrs):
        """
        Validates board membership for the requesting user, assignee, and reviewer.
        """
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
    """
    Serializer for updating an existing task.
    """
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
        """
        Returns the assignee as a formatted dictionary.
        """
        if obj.assignee:
            return {"id": obj.assignee.id, "email": obj.assignee.email, "fullname": obj.assignee.username}
        return None

    def get_reviewer(self, obj):
        """
        Returns the reviewer as a formatted dictionary.
        """
        if obj.reviewer:
            return {"id": obj.reviewer.id, "email": obj.reviewer.email, "fullname": obj.reviewer.username}
        return None

    def get_comment_count(self, obj):
        """
        Returns the total number of comments associated with the task.
        """
        return getattr(obj, 'comment_count', obj.comments.count())

    def validate(self, attrs):
        """
        Validates board membership for the newly provided assignee and reviewer.
        """
        board = self.instance.board
        assignee = attrs.get('assignee')
        reviewer = attrs.get('reviewer')
        
        if assignee and not (board.owner == assignee or board.members.filter(id=assignee.id).exists()):
            raise serializers.ValidationError({"assignee_id": "The assignee must be a member of the board."})
            
        if reviewer and not (board.owner == reviewer or board.members.filter(id=reviewer.id).exists()):
            raise serializers.ValidationError({"reviewer_id": "The reviewer must be a member of the board."})

        return attrs


class CommentListCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for listing and creating comments.
    """
    author = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'created_at', 'author', 'content']
        read_only_fields = ['author']

    def get_author(self, obj):
        """
        Returns the full name of the author, falling back to the username.
        """
        if obj.author:
            name = f"{obj.author.username}"
            return name if name else obj.author.username
        return None


class CommentDeleteSerializer(serializers.ModelSerializer):
    """
    Serializer strictly used for comment deletion.
    """
    class Meta:
        model = Comment


class EmailCheckSerializer(serializers.ModelSerializer):
    """
    Serializer to map user objects to email search results.
    """
    fullname = serializers.CharField(source='username', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'fullname']