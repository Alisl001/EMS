from rest_framework import serializers
from backend.models import Event, EventEquipment, Equipment, Wallet, TransactionLog, Category
from django.contrib.auth.models import User
from decimal import Decimal


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'username', 'email')

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class EquipmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Equipment
        fields = '__all__'

class EventEquipmentSerializer(serializers.ModelSerializer):
    equipment = EquipmentSerializer(read_only=True)
    
    class Meta:
        model = EventEquipment
        fields = '__all__'

class EventSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    equipment = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = '__all__'

    def get_equipment(self, obj):
        event_equipment = EventEquipment.objects.filter(event=obj)
        return EventEquipmentSerializer(event_equipment, many=True).data


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

        total_price = Decimal('0.00')
        for equipment_id in equipment_ids:
            equipment = Equipment.objects.get(id=equipment_id)
            total_price += equipment.rental_price
            EventEquipment.objects.create(event=event, equipment=equipment)

        event.total_price = total_price
        event.save()

        wallet = Wallet.objects.get(customer=event.user)
        if wallet.balance < total_price:
            raise serializers.ValidationError("Insufficient balance in wallet.")

        wallet.balance -= total_price
        wallet.save()

        TransactionLog.objects.create(
            customer=event.user,
            amount=total_price,
            transaction_type='purchase',
            description=f"Purchase for event: {event.name}"
        )

        return event

    def update(self, instance, validated_data):
        new_equipment_ids = validated_data.pop('equipment', None)
        
        # Get current equipment for the event
        current_event_equipment = EventEquipment.objects.filter(event=instance)
        current_equipment_ids = set(current_event_equipment.values_list('equipment_id', flat=True))

        # Calculate total price for new equipment list
        new_total_price = Decimal('0.00')
        for equipment_id in new_equipment_ids:
            equipment = Equipment.objects.get(id=equipment_id)
            new_total_price += equipment.rental_price

        # Determine equipment to add and remove
        new_equipment_ids_set = set(new_equipment_ids)
        to_add = new_equipment_ids_set - current_equipment_ids
        to_remove = current_equipment_ids - new_equipment_ids_set

        # Calculate price changes
        price_change = Decimal('0.00')
        for equipment_id in to_add:
            equipment = Equipment.objects.get(id=equipment_id)
            price_change += equipment.rental_price
            EventEquipment.objects.create(event=instance, equipment=equipment)
        
        for equipment_id in to_remove:
            equipment = Equipment.objects.get(id=equipment_id)
            price_change -= equipment.rental_price
            EventEquipment.objects.filter(event=instance, equipment=equipment).delete()

        # Adjust the wallet balance
        wallet = Wallet.objects.get(customer=instance.user)
        if price_change > Decimal('0.00') and wallet.balance < price_change:
            raise serializers.ValidationError("Insufficient balance in wallet.")

        wallet.balance -= price_change
        wallet.save()

        # Log the transaction
        transaction_type = 'refund' if price_change < Decimal('0.00') else 'purchase'
        TransactionLog.objects.create(
            customer=instance.user,
            amount=abs(price_change),
            transaction_type=transaction_type,
            description=f"Price adjustment for event: {instance.name}"
        )

        # Update the event's total price
        instance.total_price = new_total_price

        # Update other fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        return instance

