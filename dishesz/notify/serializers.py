

from rest_framework import serializers


class NotificationSerializer(serializers.ModelSerializer): 

    title = serializers.CharField(max_length=24, allow_blank=False)
    description = serializers.CharField(max_length=128, allow_blank=False)
    reffered = serializers.CharField(max_length=16)