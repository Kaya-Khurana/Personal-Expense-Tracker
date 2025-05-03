from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from .models import Expense
from .serializers import ExpenseSerializer


@api_view(['GET'])
def get_expense_choices(request):
      return Response(Expense.get_valid_choices())
# 🚀 Get All Expenses (For Admin or Debugging)

@api_view(['GET'])
def expense_list(request):
    try:
        expenses = Expense.objects.all().values("id", "amount", "category", "payment_method")
        serializer = ExpenseSerializer(expenses, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)  # ✅ Correct response format
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['DELETE'])
def delete_expense(request, expense_id):
    try:
        expense = Expense.objects.get(id=expense_id)
        expense.delete()
        return Response({"message": "Expense deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
    except Expense.DoesNotExist:
        return Response({"error": "Expense not found"}, status=status.HTTP_404_NOT_FOUND)    

# 🚀 Add Expense
@api_view(['POST'])
@permission_classes([IsAuthenticated])  # Ensures only authenticated users can add expenses
def add_expense(request):
    try:
        serializer = ExpenseSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)  # Ensure expense is linked to the logged-in user
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# 🚀 List & Create Expenses (Authenticated Users Only)
class ExpenseListCreateView(generics.ListCreateAPIView):
    serializer_class = ExpenseSerializer
    permission_classes = [IsAuthenticated]
    queryset = Expense.objects.all()

    def get_queryset(self):
        try:
            return Expense.objects.filter(user=self.request.user)
        except Exception as e:
            return Expense.objects.none()  # Return empty queryset in case of an error

    def perform_create(self, serializer):
        try:
            serializer.save(user=self.request.user)
        except Exception as e:
            raise Exception(f"Error saving expense: {str(e)}")

# 🚀 Update Expense (Authenticated Users Only)
class ExpenseUpdateView(generics.UpdateAPIView):
    serializer_class = ExpenseSerializer
    permission_classes = [IsAuthenticated]
    queryset = Expense.objects.all()

    def get_queryset(self):
        try:
            return Expense.objects.filter(user=self.request.user)
        except Exception as e:
            return Expense.objects.none()  # Handle unexpected errors

    def perform_update(self, serializer):
        try:
            serializer.save()
        except Exception as e:
            raise Exception(f"Error updating expense: {str(e)}")
    
 
# 🚀 Delete Expense (Authenticated Users Only)
class ExpenseDeleteView(generics.DestroyAPIView):
    serializer_class = ExpenseSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        try:
            return Expense.objects.filter(user=self.request.user)
        except Exception as e:
            return Expense.objects.none() 