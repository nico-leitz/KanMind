from rest_framework import permissions
from django.shortcuts import get_object_or_404
from kanmind_app.models import Task

class IsOwnerOrMember(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.method == 'DELETE':
            return obj.owner == request.user

        is_owner = obj.owner == request.user
        is_member = obj.members.filter(id=request.user.id).exists()

        return is_owner or is_member

class IsTaskMemberOrCreatorOrBoardOwner(permissions.BasePermission):
    
    def has_object_permission(self, request, view, obj):
        if request.method == 'DELETE':
            return (getattr(obj, 'creator', None) == request.user) or (obj.board.owner == request.user)

        if request.method == 'PATCH':
            is_owner = obj.board.owner == request.user
            is_member = obj.board.members.filter(id=request.user.id).exists()
            return is_owner or is_member

        return False


class IsTaskBoardMemberForComment(permissions.BasePermission):
    def has_permission(self, request, view):
        task_id = view.kwargs.get('task_id')
        if not task_id:
            return True
            
        task = get_object_or_404(Task, id=task_id)
        board = task.board
        
        is_owner = board.owner == request.user
        is_member = board.members.filter(id=request.user.id).exists()
        
        return is_owner or is_member

class IsCommentAuthor(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.author == request.user