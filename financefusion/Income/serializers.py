from rest_framework import serializers
from .models import Income

class IncomeSerializer(serializers.ModelSerializer):
    category_display = serializers.SerializerMethodField()

    class Meta:
        model = Income
        fields = '__all__'
        read_only_fields = ['category_display']

    def get_category_display(self, obj):
        return obj.get_category_display()