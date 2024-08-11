from rest_framework import serializers
from django.contrib.auth.models import User

class UserRegistrationSerializer(serializers.ModelSerializer):
    role = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'username', 'password', 'role']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        role = validated_data.pop('role')
        user = User.objects.create(**validated_data)
        user.set_password(validated_data['password'])

        if role == 'admin':
            user.is_superuser = True
        user.save()
        return user

class CustomAuthTokenSerializer(serializers.Serializer):
    username = serializers.CharField(label="Username")
    password = serializers.CharField(label="Password", style={'input_type': 'password'}, trim_whitespace=False)

    def validate(self, attrs):
        from django.contrib.auth import authenticate
        username = attrs.get('username')
        password = attrs.get('password')

        if username and password:
            user = authenticate(request=self.context.get('request'), username=username, password=password)
            if not user:
                raise serializers.ValidationError('Unable to log in with provided credentials.', code='authorization')
        else:
            raise serializers.ValidationError('Must include "username" and "password".', code='authorization')

        attrs['user'] = user
        return attrs

class UserLoginResponseSerializer(serializers.Serializer):
    access_token = serializers.CharField()
    token_type = serializers.CharField()
    expires_in = serializers.IntegerField()
    user = serializers.SerializerMethodField()

    def get_user(self, obj):
        return {
            'id': obj['user']['id'],
            'first_name': obj['user']['first_name'],
            'last_name': obj['user']['last_name'],
            'username': obj['user']['username'],
            'email': obj['user']['email'],
            'date_joined': obj['user']['date_joined'],
            'role': obj['user']['role'],
        }

class CustomUserSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'username', 'email', 'date_joined', 'role']

    def get_role(self, obj):
        if obj.is_superuser:
            return 'admin'
        else:
            return 'customer'
