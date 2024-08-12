from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from users.authentication import BearerTokenAuthentication
from backend.models import Wallet, TransactionLog
from .serializers import WalletSerializer, TransactionLogSerializer
from django.contrib.auth.models import User
from decimal import Decimal


# View My Wallet API
@api_view(['GET'])
@authentication_classes([BearerTokenAuthentication])
@permission_classes([IsAuthenticated])
def viewWallet(request):
    wallet, created = Wallet.objects.get_or_create(customer=request.user)
    serializer = WalletSerializer(wallet)
    return Response(serializer.data)


# Add Funds API
@api_view(['POST'])
@authentication_classes([BearerTokenAuthentication])
@permission_classes([IsAdminUser])
def addFunds(request):
    username = request.data.get('username')
    amount = request.data.get('amount')

    if not (username and amount):
        return Response({"detail": "Incomplete data provided"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    try:
        wallet, created = Wallet.objects.get_or_create(customer=user)
        wallet.balance += Decimal(amount)
        wallet.save()

        TransactionLog.objects.create(
            customer=user,
            amount=amount,
            transaction_type='deposit',
            description='Added funds to wallet'
        )

        return Response({"detail": "Funds added successfully"}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"detail": f"Error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

# My Transaction Log API
@api_view(['GET'])
@authentication_classes([BearerTokenAuthentication])
@permission_classes([IsAuthenticated])
def myTransactionLog(request):
    user = request.user
    transaction_logs = TransactionLog.objects.filter(customer=user).order_by('-timestamp')
    serializer = TransactionLogSerializer(transaction_logs, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

