from django.urls import path
from .views import BoardListView, BoardDetailView, TaskCreateView ,TaskDetailView

urlpatterns = [
    path('boards/', BoardListView.as_view(), name='board-list-create'),
    path('boards/<int:pk>/', BoardDetailView.as_view(), name='board-detail'),
    path('tasks/', TaskCreateView.as_view(), name='task-create'),
    path('tasks/<int:pk>/', TaskDetailView.as_view(), name='task-detail')
]