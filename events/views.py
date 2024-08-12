from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from backend.models import Event
from .serializers import EventSerializer, EventCreationSerializer
from users.authentication import BearerTokenAuthentication
from rest_framework import status
from django.utils import timezone


# Helper function to update event status
def update_event_status(event):
    now = timezone.now()
    event_start = timezone.datetime.combine(event.date, event.start_time)
    event_end = timezone.datetime.combine(event.date, event.end_time)

    if now < event_start:
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
        return Response(serializer.data, status=status.HTTP_201_CREATED)
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
    
    serializer = EventCreationSerializer(event, data=request.data)
    if serializer.is_valid():
        serializer.save()
        update_event_status(event) 
        return Response(serializer.data, status=status.HTTP_200_OK)
    
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
    
    event.status = 'canceled'
    event.save()
    
    return Response({'detail': 'Event has been canceled.'}, status=status.HTTP_200_OK)


