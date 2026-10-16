from django.urls import path
from .views import BoardListView, BoardDetailView, TaskCreateView ,TaskDetailView, EmailCheckView, CommentListCreateView, CommentDeleteView, TaskAssignedToMeListView, TaskReviewingListView

urlpatterns = [
    path('boards/', BoardListView.as_view(), name='board-list-create'),
    path('boards/<int:pk>/', BoardDetailView.as_view(), name='board-detail'),
    path('email-check/', EmailCheckView.as_view(), name='email-check'),
    path('tasks/assigned-to-me/', TaskAssignedToMeListView.as_view(), name='task-assigned-to-me'),
    path('tasks/reviewing/', TaskReviewingListView.as_view(), name='task-reviewing'),
    path('tasks/', TaskCreateView.as_view(), name='task-create'),
    path('tasks/<int:task_id>/comments/', CommentListCreateView.as_view(), name='task-comment-list-create'),
    path('tasks/<int:task_id>/comments/<int:comment_id>/', CommentDeleteView.as_view(), name='task-comment-delete'),
    path('tasks/<int:pk>/', TaskDetailView.as_view(), name='task-detail'),
]