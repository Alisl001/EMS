from rest_framework import serializers
from backend.models import Wallet, TransactionLog
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'username', 'email')

class WalletSerializer(serializers.ModelSerializer):
    customer = UserSerializer()  

    class Meta:
        model = Wallet
        fields = '__all__'

class TransactionLogSerializer(serializers.ModelSerializer):
    customer = UserSerializer()  

    class Meta:
        model = TransactionLog
        fields = '__all__'