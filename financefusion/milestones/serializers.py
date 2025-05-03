from rest_framework import serializers
from .models import Milestone

class MilestoneSerializer(serializers.ModelSerializer):
    progress_percentage = serializers.SerializerMethodField()
    days_until_deadline = serializers.SerializerMethodField()
    is_overdue = serializers.SerializerMethodField()

    class Meta:
        model = Milestone
        fields = '__all__'
        read_only_fields = ['user', 'current_amount', 'status', 'created_at', 'updated_at', 'progress_percentage', 'days_until_deadline', 'is_overdue']

    def get_progress_percentage(self, obj):
        return obj.progress_percentage()

    def get_days_until_deadline(self, obj):
        return obj.days_until_deadline()

    def get_is_overdue(self, obj):
        return obj.is_overdue()