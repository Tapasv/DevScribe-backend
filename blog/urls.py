from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    PostViewSet, 
    CategoryViewSet, 
    CommentViewSet,
    register,
    login,
    logout,
    UserProfileView,
    ChangePasswordView,
    health_check
)

router = DefaultRouter()
router.register(r'posts', PostViewSet, basename='post')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'comments', CommentViewSet, basename='comment')

urlpatterns = [
    path('', include(router.urls)),
    
    # Auth endpoints
    path('auth/register/', register, name='register'),
    path('auth/login/', login, name='login'),
    path('auth/logout/', logout, name='logout'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/change-password/', ChangePasswordView.as_view(), name='change_password'),
    
    # Profile
    path('profile/', UserProfileView.as_view(), name='profile'),
    
    path('health/', health_check, name='health_check')
]