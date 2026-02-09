from rest_framework import viewsets, filters, status, permissions, generics
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.db.models import Count, Q
from .models import Post, Category, Comment, UserProfile
from .serializers import (
    PostListSerializer, 
    PostDetailSerializer, 
    PostCreateUpdateSerializer,
    CategorySerializer, 
    CommentSerializer,
    UserSerializer,
    UserProfileSerializer,
    RegisterSerializer,
    ChangePasswordSerializer
)

class IsAuthorOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user

class IsAuthorRole(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.profile.role == 'author'

# Authentication Views
@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': UserSerializer(user).data,
            'profile': UserProfileSerializer(user.profile).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    username = request.data.get('username')
    password = request.data.get('password')
    
    user = authenticate(username=username, password=password)
    
    if user:
        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserSerializer(user).data,
            'profile': UserProfileSerializer(user.profile).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        })
    return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    try:
        refresh_token = request.data.get('refresh_token')
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response({'message': 'Logout successful'}, status=status.HTTP_200_OK)
    except Exception:
        return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)

class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        return self.request.user.profile

class ChangePasswordView(generics.UpdateAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated]
    
    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = request.user
        if not user.check_password(serializer.data.get('old_password')):
            return Response({'error': 'Wrong password'}, status=status.HTTP_400_BAD_REQUEST)
        
        user.set_password(serializer.data.get('new_password'))
        user.save()
        
        return Response({'message': 'Password updated successfully'}, status=status.HTTP_200_OK)

class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.filter(published=True).select_related('author', 'category')
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'content', 'excerpt']
    ordering_fields = ['created_at', 'title', 'views']
    lookup_field = 'slug'
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return PostCreateUpdateSerializer
        elif self.action == 'retrieve':
            return PostDetailSerializer
        return PostListSerializer
    
    def get_permissions(self):
        if self.action in ['create']:
            return [IsAuthenticated(), IsAuthorRole()]
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsAuthorOrReadOnly()]
        return [AllowAny()]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # If user is authenticated, show their unpublished posts too
        if self.request.user.is_authenticated:
            queryset = Post.objects.filter(
                Q(published=True) | Q(author=self.request.user)
            ).select_related('author', 'category')
        
        return queryset
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        # Only increment views for non-authors
        if not request.user.is_authenticated or instance.author != request.user:
            instance.views += 1
            instance.save(update_fields=['views'])
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def my_posts(self, request):
        if not request.user.is_authenticated:
            return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
        
        posts = Post.objects.filter(author=request.user).select_related('category')
        page = self.paginate_queryset(posts)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(posts, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def featured(self, request):
        featured_posts = self.queryset.filter(featured=True)[:5]
        serializer = self.get_serializer(featured_posts, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_category(self, request):
        category_slug = request.query_params.get('category')
        if category_slug:
            posts = self.queryset.filter(category__slug=category_slug)
            page = self.paginate_queryset(posts)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            serializer = self.get_serializer(posts, many=True)
            return Response(serializer.data)
        return Response({'error': 'Category parameter required'}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def popular(self, request):
        popular_posts = self.queryset.order_by('-views')[:5]
        serializer = self.get_serializer(popular_posts, many=True)
        return Response(serializer.data)

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.annotate(
        post_count=Count('posts', filter=Q(posts__published=True))
    )
    serializer_class = CategorySerializer
    lookup_field = 'slug'

class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.filter(approved=True)
    serializer_class = CommentSerializer
    permission_classes = [AllowAny]
    http_method_names = ['get', 'post']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        post_slug = self.request.query_params.get('post')
        if post_slug:
            queryset = queryset.filter(post__slug=post_slug)
        return queryset
    
    def perform_create(self, serializer):
        if self.request.user.is_authenticated:
            serializer.save(
                user=self.request.user,
                name=self.request.user.get_full_name() or self.request.user.username,
                email=self.request.user.email
            )
        else:
            serializer.save()
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(
            {'message': 'Comment submitted successfully! It will appear after approval.'},
            status=status.HTTP_201_CREATED
        )