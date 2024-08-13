from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, get_user_model


UserModel = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    role = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)  # Add this field

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'username', 'password', 'role', 'confirm_password']  # Include confirm_password
        extra_kwargs = {'password': {'write_only': True}}

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with that email already exists.")
        return value

    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        role = validated_data.pop('role', 'customer')
        user = User.objects.create_user(
            **validated_data,
            is_staff=(role == 'staff' or role == 'admin'),
            is_superuser=(role == 'admin'),
        )
        return user


class CustomAuthTokenSerializer(serializers.Serializer):
    
    username_or_email = serializers.CharField(label="Username or Email")
    password = serializers.CharField(label="Password", style={'input_type': 'password'})

    def validate(self, attrs):
        username_or_email = attrs.get('username_or_email')
        password = attrs.get('password')

        user = None

        # Check if the input is an email
        if '@' in username_or_email:
            try:
                user = UserModel.objects.get(email=username_or_email)
            except UserModel.DoesNotExist:
                pass  

        if not user:
            user = authenticate(request=self.context.get('request'), username=username_or_email, password=password)

        if not user:
            raise serializers.ValidationError({'detail':'Unable to log in with provided credentials.'})

        attrs['user'] = user
        return attrs

class UserLoginResponseSerializer(serializers.Serializer):
    access_token = serializers.CharField()
    token_type = serializers.CharField()
    expires_in = serializers.IntegerField()
    user = serializers.DictField(child=serializers.CharField())

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['user']['date_joined'] = instance.user.date_joined.isoformat()
        return representation


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


class UserInfoUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email']

    def validate(self, data):
        username = data.get('username')
        if User.objects.exclude(pk=self.instance.pk).filter(username=username).exists():
            raise serializers.ValidationError("Username is already in use.")

        email = data.get('email')
        if User.objects.exclude(pk=self.instance.pk).filter(email=email).exists():
            raise serializers.ValidationError("Email is already in use.")

        return data
