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
    
    serializer_class = BoardListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return boards_with_counts().filter(
            Q(owner=user) | Q(members=user)
        ).distinct()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        board = serializer.save(owner=request.user)
        
        board_with_counts = boards_with_counts().get(pk=board.pk)
        output = self.get_serializer(board_with_counts).data
        return Response(output, status=status.HTTP_201_CREATED)


class BoardDetailView(generics.RetrieveUpdateDestroyAPIView):
    
    serializer_class = BoardDetailSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrMember]
    http_method_names = ['get', 'patch', 'delete', 'head', 'options']

    def get_queryset(self):
        return Board.objects.filter(
            Q(owner=self.request.user) | Q(members=self.request.user)
        ).distinct()

    def get_serializer_class(self):
        if self.request.method == 'PATCH':
            return BoardUpdateSerializer
        return BoardDetailSerializer


class TaskCreateView(generics.CreateAPIView):
    
    serializer_class = TaskCreateSerializer
    permission_classes = [IsAuthenticated] 

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)


class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    
    queryset = Task.objects.select_related('assignee', 'reviewer').annotate(
        comment_count=Count('comments', distinct=True)
    )
    serializer_class = TaskUpdateSerializer
    permission_classes = [IsAuthenticated, IsTaskMemberOrCreatorOrBoardOwner]
    http_method_names = ['patch', 'delete']


class CommentListCreateView(generics.ListCreateAPIView):
    
    serializer_class = CommentListCreateSerializer
    permission_classes = [IsAuthenticated, IsTaskBoardMemberForComment]

    def get_queryset(self):
        task_id = self.kwargs.get('task_id')
        return Comment.objects.select_related('author').filter(task_id=task_id).order_by('created_at')

    def perform_create(self, serializer):
        task_id = self.kwargs.get('task_id')
        task = get_object_or_404(Task, id=task_id)
        serializer.save(author=self.request.user, task=task)


class CommentDeleteView(generics.DestroyAPIView):
    
    serializer_class = CommentDeleteSerializer
    permission_classes = [IsAuthenticated, IsCommentAuthor]
    lookup_url_kwarg = 'comment_id'

    def get_queryset(self):
        task_id = self.kwargs.get('task_id')
        return Comment.objects.filter(task_id=task_id)


class EmailCheckView(generics.RetrieveAPIView):
    
    serializer_class = EmailCheckSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        email = self.request.query_params.get("email")
        if not email:
            raise ValidationError({"detail": "email parameter is missing."})
        return get_object_or_404(User, email=email)


class TaskAssignedToMeListView(generics.ListAPIView):
    
    serializer_class = TaskUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Task.objects.select_related('assignee', 'reviewer').annotate(
            comment_count=Count('comments', distinct=True)
        ).filter(assignee=self.request.user)


class TaskReviewingListView(generics.ListAPIView):
    
    serializer_class = TaskUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Task.objects.select_related('assignee', 'reviewer').annotate(
            comment_count=Count('comments', distinct=True)
        ).filter(reviewer=self.request.user)