from rest_framework import serializers
from .models import Post, Category, Comment, UserProfile
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password


# ================= USER =================

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']


class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')

    class Meta:
        model = UserProfile
        fields = [
            'id','username','email','first_name','last_name','role',
            'bio','avatar','website','location','total_posts',
            'total_views','total_comments','created_at'
        ]
        read_only_fields = ['role','total_posts','total_views','total_comments']

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', {})

        if user_data:
            user = instance.user
            user.first_name = user_data.get('first_name', user.first_name)
            user.last_name = user_data.get('last_name', user.last_name)
            user.save()

        return super().update(instance, validated_data)


# ================= AUTH =================

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True)
    role = serializers.ChoiceField(choices=['reader','author'], default='reader')

    class Meta:
        model = User
        fields = ('username','email','password','password2','first_name','last_name','role')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Passwords don't match"})

        if User.objects.filter(email=attrs['email']).exists():
            raise serializers.ValidationError({"email": "Email already exists"})

        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        role = validated_data.pop('role','reader')

        user = User.objects.create_user(**validated_data)
        user.profile.role = role
        user.profile.save()

        return user


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField()
    new_password = serializers.CharField(validators=[validate_password])


# ================= CATEGORY =================

class CategorySerializer(serializers.ModelSerializer):
    post_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id','name','slug','description','post_count','created_at']

    def get_post_count(self, obj):
        return obj.posts.filter(published=True).count()


# ================= COMMENTS =================

class CommentSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id','post','user','name','email','content','created_at','approved','user_name']
        read_only_fields = ['created_at','approved','user']

    def get_user_name(self, obj):
        return obj.user.username if obj.user else obj.name


# ================= POSTS =================

class PostListSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    comment_count = serializers.SerializerMethodField()
    is_author = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            'id','title','slug','author','excerpt','category',
            'image','created_at','updated_at','featured','views',
            'comment_count','is_author'
        ]

    def get_image(self, obj):
        request = self.context.get('request')
        if obj.image:
            return request.build_absolute_uri(obj.image.url)
        return None

    def get_comment_count(self, obj):
        return obj.comments.filter(approved=True).count()

    def get_is_author(self, obj):
        request = self.context.get('request')
        return request.user == obj.author if request and request.user.is_authenticated else False


class PostDetailSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    comment_count = serializers.SerializerMethodField()
    is_author = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            'id','title','slug','author','content','excerpt','category',
            'image','created_at','updated_at','featured','views',
            'comments','comment_count','is_author'
        ]

    def get_image(self, obj):
        request = self.context.get('request')
        if obj.image:
            return request.build_absolute_uri(obj.image.url)
        return None

    def get_comment_count(self, obj):
        return obj.comments.filter(approved=True).count()

    def get_is_author(self, obj):
        request = self.context.get('request')
        return request.user == obj.author if request and request.user.is_authenticated else False


class PostCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['id','title','slug','content','excerpt','category','image','published','featured']
        read_only_fields = ['slug']

    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)
