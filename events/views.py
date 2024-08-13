from ast import Not
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from backend.models import Event
from .serializers import EventSerializer, EventCreationSerializer
from users.authentication import BearerTokenAuthentication
from rest_framework import status
from django.utils import timezone
from backend.models import Wallet, TransactionLog, Equipment, EventEquipment


# Helper function to update event status
def update_event_status(event):
    now = timezone.now()
    
    # Combine date and time, and make them timezone-aware
    event_start = timezone.make_aware(timezone.datetime.combine(event.date, event.start_time), timezone.get_current_timezone())
    event_end = timezone.make_aware(timezone.datetime.combine(event.date, event.end_time), timezone.get_current_timezone())

    if event.status == 'canceled':
        event.status == 'canceled'
    elif now < event_start:
        event.status = 'upcoming'
    elif event_start <= now <= event_end:
        event.status = 'ongoing'
    else:
        event.status = 'completed'
    event.save()


# List all events (Admin only)
@api_view(['GET'])
@authentication_classes([BearerTokenAuthentication])
@permission_classes([IsAuthenticated, IsAdminUser])
def list_all_events(request):
    events = Event.objects.all().order_by('-date')

    # Update the status of each event based on the current time
    for event in events:
        update_event_status(event)
        
    serializer = EventSerializer(events, many=True)
    return Response(serializer.data)


# List my events (Customer)
@api_view(['GET'])
@authentication_classes([BearerTokenAuthentication])
@permission_classes([IsAuthenticated])
def list_my_events(request):
    user = request.user
    events = Event.objects.filter(user=user).order_by('-date')

    # Update the status of each event based on the current time
    for event in events:
        update_event_status(event)
        
    serializer = EventSerializer(events, many=True)
    return Response(serializer.data)


# Create event 
@api_view(['POST'])
@authentication_classes([BearerTokenAuthentication])
@permission_classes([IsAuthenticated])
def create_event(request):
    serializer = EventCreationSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(user=request.user)
        return Response({"detail": "Event created successfully."}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Update Event (Customer)
@api_view(['PUT'])
@authentication_classes([BearerTokenAuthentication])
@permission_classes([IsAuthenticated])
def update_event(request, pk):
    try:
        event = Event.objects.get(pk=pk, user=request.user)
    except Event.DoesNotExist:
        return Response({'detail': 'Event not found or you do not have permission to update this event.'}, status=status.HTTP_404_NOT_FOUND)

    # Pass the instance and the request data to the serializer
    serializer = EventCreationSerializer(instance=event, data=request.data, partial=True)
    
    if serializer.is_valid():
        # Let the serializer handle the update logic
        serializer.save()
        return Response({"detail": "Event updated successfully."}, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Cancel Event (Customer)
@api_view(['POST'])
@authentication_classes([BearerTokenAuthentication])
@permission_classes([IsAuthenticated])
def cancel_event(request, pk):
    try:
        event = Event.objects.get(pk=pk, user=request.user)
    except Event.DoesNotExist:
        return Response({'detail': 'Event not found or you do not have permission to cancel this event.'}, status=status.HTTP_404_NOT_FOUND)
    
    wallet = Wallet.objects.get(customer=event.user)
    wallet.balance += event.total_price
    wallet.save()

    # Log the refund transaction
    TransactionLog.objects.create(
        customer=event.user,
        amount=event.total_price,
        transaction_type='refund',
        description=f"Refund for canceled event: {event.name}"
    )

    EventEquipment.objects.filter(event=event).delete()
    
    event.status = 'canceled'
    event.save()
    
    return Response({'detail': 'Event has been canceled and a refund has been issued.'}, status=status.HTTP_200_OK)


