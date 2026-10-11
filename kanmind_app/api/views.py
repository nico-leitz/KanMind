from django.db.models import Q
from rest_framework import generics
from django.contrib.auth.models import User
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.permissions import IsAuthenticated
from kanmind_app.models import Board, Task
from .serializers import BoardListSerializer, BoardDetailSerializer, BoardUpdateSerializer, TaskSerializer, EmailCheckSerializer
from .permissions import IsOwnerOrMember, IsTaskMemberOrCreatorOrBoardOwner

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
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, IsTaskMemberOrCreatorOrBoardOwner] 

class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, IsTaskMemberOrCreatorOrBoardOwner]
    http_method_names = ['patch', 'delete']


class EmailCheckView(generics.RetrieveAPIView):
    serializer_class = EmailCheckSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        email = self.request.query_params.get('email')

        if not email:
            raise ValidationError({"detail": "email parameter is missing."})

        user = User.objects.filter(email=email).first()

        if not user:
            raise NotFound({"detail": "email could not be found."})

        return user

