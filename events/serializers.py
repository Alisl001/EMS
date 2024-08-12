from rest_framework import serializers
from backend.models import Event, EventEquipment, Equipment

class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = '__all__'

class EventEquipmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventEquipment
        fields = '__all__'

class EventCreationSerializer(serializers.ModelSerializer):
    equipment = serializers.ListField(
        child=serializers.IntegerField(), write_only=True
    )

    class Meta:
        model = Event
        fields = ['name', 'description', 'date', 'start_time', 'end_time', 'location', 'capacity', 'category', 'status', 'equipment']

    def create(self, validated_data):
        equipment_ids = validated_data.pop('equipment')
        event = Event.objects.create(**validated_data)
        
        for equipment_id in equipment_ids:
            equipment = Equipment.objects.get(id=equipment_id)
            EventEquipment.objects.create(event=event, equipment=equipment)
        
        return event
