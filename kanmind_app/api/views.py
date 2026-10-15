from django.db.models import Q
from rest_framework import generics
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.permissions import IsAuthenticated
from kanmind_app.models import Board, Task, Comment
from .serializers import BoardListSerializer, BoardDetailSerializer, BoardUpdateSerializer, TaskCreateSerializer, EmailCheckSerializer, TaskUpdateSerializer, CommentListCreateSerializer, CommentDeleteSerializer
from .permissions import IsOwnerOrMember, IsTaskMemberOrCreatorOrBoardOwner, IsCommentAuthor, IsTaskBoardMemberForComment

class BoardListView(generics.ListCreateAPIView):
    serializer_class = BoardListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Board.objects.filter(
            Q(owner=self.request.user) | Q(members=self.request.user)
        ).distinct()

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

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
    queryset = Task.objects.all()
    serializer_class = TaskUpdateSerializer
    permission_classes = [IsAuthenticated, IsTaskMemberOrCreatorOrBoardOwner]
    http_method_names = ['patch', 'delete']


class CommentListCreateView(generics.ListCreateAPIView):
    serializer_class = CommentListCreateSerializer
    permission_classes = [IsAuthenticated, IsTaskBoardMemberForComment]

    def get_queryset(self):
        task_id = self.kwargs.get('task_id')
        return Comment.objects.filter(task_id=task_id).order_by('created_at')

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
        return Task.objects.filter(assignee=self.request.user)


class TaskReviewingListView(generics.ListAPIView):
    serializer_class = TaskUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Task.objects.filter(reviewer=self.request.user)

