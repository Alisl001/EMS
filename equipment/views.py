from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from backend.models import Equipment
from .serializers import EquipmentSerializer
from users.authentication import BearerTokenAuthentication


# Create equipment (Admin only)
@api_view(['POST'])
@authentication_classes([BearerTokenAuthentication])
@permission_classes([IsAuthenticated, IsAdminUser])
def create_equipment(request):
    serializer = EquipmentSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Update equipment (Admin only)
@api_view(['PUT'])
@authentication_classes([BearerTokenAuthentication])
@permission_classes([IsAuthenticated, IsAdminUser])
def update_equipment(request, pk):
    try:
        equipment = Equipment.objects.get(pk=pk)
    except Equipment.DoesNotExist:
        return Response({'detail': 'Equipment not found.'}, status=status.HTTP_404_NOT_FOUND)

    serializer = EquipmentSerializer(equipment, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Delete equipment (Admin only)
@api_view(['DELETE'])
@authentication_classes([BearerTokenAuthentication])
@permission_classes([IsAuthenticated, IsAdminUser])
def delete_equipment(request, pk):
    try:
        equipment = Equipment.objects.get(pk=pk)
    except Equipment.DoesNotExist:
        return Response({'detail': 'Equipment not found.'}, status=status.HTTP_404_NOT_FOUND)

    equipment.delete()
    return Response({'detail': 'Equipment deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)


# List all equipment (Accessible to all users)
@api_view(['GET'])
@authentication_classes([BearerTokenAuthentication])
@permission_classes([IsAuthenticated])
def list_equipment(request):
    equipment = Equipment.objects.all()
    serializer = EquipmentSerializer(equipment, many=True)
    return Response(serializer.data)

