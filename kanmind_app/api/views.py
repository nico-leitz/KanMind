from django.db.models import Q, Count
from rest_framework import generics, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.permissions import IsAuthenticated
from kanmind_app.models import Board, Task, Comment
from .serializers import (
    BoardListSerializer, BoardDetailSerializer, BoardUpdateSerializer, 
    TaskCreateSerializer, EmailCheckSerializer, TaskUpdateSerializer, 
    CommentListCreateSerializer, CommentDeleteSerializer
)
from .permissions import (
    IsOwnerOrMember, IsTaskMemberOrCreatorOrBoardOwner, 
    IsCommentAuthor, IsTaskBoardMemberForComment
)


def boards_with_counts():
    """
    Returns a board queryset that calculates all counts directly in the database.
    """
    return Board.objects.annotate(
        member_count=Count('members', distinct=True),
        ticket_count=Count('tasks', distinct=True),
        tasks_to_do_count=Count(
            'tasks', filter=Q(tasks__status='to-do'), distinct=True
        ),
        tasks_high_prio_count=Count(
            'tasks', filter=Q(tasks__priority='high'), distinct=True
        ),
    )


class BoardListView(generics.ListCreateAPIView):
    """
    API view to retrieve a list of boards or create a new board.
    """
    serializer_class = BoardListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Returns all boards where the user is either the owner or a member.
        """
        user = self.request.user
        return boards_with_counts().filter(
            Q(owner=user) | Q(members=user)
        ).distinct()

    def create(self, request, *args, **kwargs):
        """
        Creates a board and reloads it to ensure annotated counts are present.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        board = serializer.save(owner=request.user)
        
        board_with_counts = boards_with_counts().get(pk=board.pk)
        output = self.get_serializer(board_with_counts).data
        return Response(output, status=status.HTTP_201_CREATED)


class BoardDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API view to retrieve, update, or delete a specific board.
    """
    serializer_class = BoardDetailSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrMember]
    http_method_names = ['get', 'patch', 'delete', 'head', 'options']

    def get_queryset(self):
        """
        Limits the accessible boards to those owned by or joined by the user.
        (Updated to .all() to allow permission classes to throw 403 instead of 404)
        """
        return Board.objects.all()

    def get_serializer_class(self):
        """
        Switches dynamically to the update serializer for PATCH requests.
        """
        if self.request.method == 'PATCH':
            return BoardUpdateSerializer
        return BoardDetailSerializer


class TaskCreateView(generics.CreateAPIView):
    """
    API view to create a new task within a board.
    """
    serializer_class = TaskCreateSerializer
    permission_classes = [IsAuthenticated] 

    def perform_create(self, serializer):
        """
        Saves the new task and explicitly sets the creator field.
        """
        serializer.save(creator=self.request.user)


class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API view to update or delete a specific task.
    """
    queryset = Task.objects.select_related('assignee', 'reviewer').annotate(
        comments_count=Count('comments', distinct=True)
    )
    serializer_class = TaskUpdateSerializer
    permission_classes = [IsAuthenticated, IsTaskMemberOrCreatorOrBoardOwner]
    http_method_names = ['patch', 'delete']


class CommentListCreateView(generics.ListCreateAPIView):
    """
    API view to list all comments for a specific task or create a new comment.
    """
    serializer_class = CommentListCreateSerializer
    permission_classes = [IsAuthenticated, IsTaskBoardMemberForComment]

    def get_queryset(self):
        """
        Retrieves chronologically ordered comments associated with the given task ID.
        """
        task_id = self.kwargs.get('task_id')
        return Comment.objects.select_related('author').filter(task_id=task_id).order_by('created_at')

    def perform_create(self, serializer):
        """
        Assigns the requesting user as author and links the specified task upon creation.
        """
        task_id = self.kwargs.get('task_id')
        task = get_object_or_404(Task, id=task_id)
        serializer.save(author=self.request.user, task=task)


class CommentDeleteView(generics.DestroyAPIView):
    """
    API view to delete a specific comment.
    """
    serializer_class = CommentDeleteSerializer
    permission_classes = [IsAuthenticated, IsCommentAuthor]
    lookup_url_kwarg = 'comment_id'

    def get_queryset(self):
        """
        Ensures the comment belongs to the specified task before deletion.
        """
        task_id = self.kwargs.get('task_id')
        return Comment.objects.filter(task_id=task_id)


class EmailCheckView(generics.RetrieveAPIView):
    """
    API view to query a user by their email address.
    """
    serializer_class = EmailCheckSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        """
        Retrieves the user based on the provided email query parameter.
        """
        email = self.request.query_params.get("email")
        if not email:
            raise ValidationError({"detail": "email parameter is missing."})
        return get_object_or_404(User, email=email)


class TaskAssignedToMeListView(generics.ListAPIView):
    """
    API view to list all tasks assigned to the currently authenticated user.
    """
    serializer_class = TaskUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Filters tasks specifically by the assignee field.
        """
        return Task.objects.select_related('assignee', 'reviewer').annotate(
            comments_count=Count('comments', distinct=True)
        ).filter(assignee=self.request.user)


class TaskReviewingListView(generics.ListAPIView):
    """
    API view to list all tasks where the authenticated user acts as the reviewer.
    """
    serializer_class = TaskUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Filters tasks specifically by the reviewer field.
        """
        return Task.objects.select_related('assignee', 'reviewer').annotate(
            comments_count=Count('comments', distinct=True)
        ).filter(reviewer=self.request.user)