from rest_framework import serializers
from .models import Expense

class ExpenseSerializer(serializers.ModelSerializer):
    category_display = serializers.SerializerMethodField()
    payment_method_display = serializers.SerializerMethodField()

    class Meta:
        model = Expense
        fields = '__all__'
        read_only_fields = ['category_display', 'payment_method_display']

    def get_category_display(self, obj):
        return obj.get_category_display()

    def get_payment_method_display(self, obj):
        return obj.get_payment_method_display()