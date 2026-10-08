from rest_framework import permissions

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