from rest_framework import serializers
from .models import User, Ride, DriverLocation, Payment, OTP


class UserLoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    class Meta:
        model = User
        fields = '__all__'
    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

class RideSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    driver_name = serializers.CharField(source="driver.username", read_only=True)

    class Meta:
        model = Ride
        fields = '__all__'
        read_only_fields = [
            'user','driver','status','fare','completed',
            'paid','created_at','completed_at'
        ]
        # Add the extra fields to output
        extra_fields = ['username', 'driver_name']

    def to_representation(self, instance):
        # include both default + extra fields
        rep = super().to_representation(instance)
        rep['username'] = instance.user.username if instance.user else None
        rep['driver_name'] = instance.driver.username if instance.driver else None
        return rep


class DriverLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = DriverLocation
        fields = '__all__'
        read_only_fields = ['driver','updated_at']

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'
        read_only_fields = ['user','ride','razorpay_order_id','paid']

class SendOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()

class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=6)

class RideFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ride
        fields = ['id', 'rating', 'feedback']
        read_only_fields = ['id']
 
    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value

class UserEditSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"
        extra_kwargs = {
            "username": {"validators": []}  
        }

class AdminRideSerializer(serializers.ModelSerializer):
    userName = serializers.CharField(source='user.username', read_only=True)
    driverName = serializers.CharField(source='driver.username', read_only=True)
    rejectedByIds = serializers.PrimaryKeyRelatedField(many=True, source='rejected_by', read_only=True)

    class Meta:
        model = Ride
        fields = [
            'id', 'pickup', 'drop', 'fare', 'status', 'completed', 'paid',
            'created_at', 'completed_at', 'rating', 'feedback', 'user', 'driver',
            'userName', 'driverName', 'rejectedByIds'
        ]    

class DriverPingSerializer(serializers.ModelSerializer):
    class Meta:
        model = DriverLocation
        fields = ["latitude", "longitude"]

from rest_framework import serializers
from .models import FareRule

class FareRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = FareRule
        fields = "__all__"
        

# serializers.py
from rest_framework import serializers
from .models import DistanceReward, TourismOffer

class DistanceRewardSerializer(serializers.ModelSerializer):
    class Meta:
        model = DistanceReward
        fields = "__all__"

class TourismOfferSerializer(serializers.ModelSerializer):
    class Meta:
        model = TourismOffer
        fields = "__all__"
    