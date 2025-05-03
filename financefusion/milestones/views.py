# financefusion/milestones/views.py
import decimal
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from .models import Milestone
from .serializers import MilestoneSerializer
from django.utils import timezone

# List & Create Milestones
class MilestoneListCreateView(generics.ListCreateAPIView):
    serializer_class = MilestoneSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Milestone.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

# Update Milestone
class MilestoneUpdateView(generics.UpdateAPIView):
    serializer_class = MilestoneSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Milestone.objects.filter(user=self.request.user)

# Delete Milestone
class MilestoneDeleteView(generics.DestroyAPIView):
    queryset = Milestone.objects.all()
    serializer_class = MilestoneSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_milestone_progress(request, pk):
    try:
        milestone = Milestone.objects.get(id=pk, user=request.user)
        amount = request.data.get('amount', 0)
        # Convert amount to Decimal instead of float
        amount = decimal.Decimal(str(amount))
        if amount <= 0:
            return Response({"error": "Amount must be positive"}, status=status.HTTP_400_BAD_REQUEST)

        milestone.current_amount += amount  # Now both are Decimal, so this should work
        if milestone.current_amount >= milestone.target_amount:
            milestone.status = 'completed'
        elif milestone.is_overdue():
            milestone.status = 'failed'
        milestone.save()
        serializer = MilestoneSerializer(milestone)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Milestone.DoesNotExist:
        return Response({"error": "Milestone not found"}, status=status.HTTP_404_NOT_FOUND)
    except (ValueError, decimal.InvalidOperation):
        return Response({"error": "Invalid amount"}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_milestone(request, pk):
    try:
        milestone = Milestone.objects.get(id=pk, user=request.user)
        print("Original milestone:", milestone.__dict__)
        serializer = MilestoneSerializer(milestone, data=request.data, partial=True)
        if serializer.is_valid():
            updated_milestone = serializer.save()
            print("Updated milestone:", updated_milestone.__dict__)
            # Force a refresh from the database to confirm the update
            updated_milestone.refresh_from_db()
            print("Refreshed milestone from DB:", updated_milestone.__dict__)
            return Response(MilestoneSerializer(updated_milestone).data, status=status.HTTP_200_OK)
        print("Serializer errors:", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Milestone.DoesNotExist:
        return Response({"error": "Milestone not found"}, status=status.HTTP_404_NOT_FOUND)