from django.urls import path
from .views import BoardListView, BoardDetailView, RegisterView, LoginView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('boards/', BoardListView.as_view(), name='board-list-create'),
    path('boards/<int:pk>/', BoardDetailView.as_view(), name='board-detail')
]
