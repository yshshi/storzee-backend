# apps/wallet/views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .models import UserWallet, SaathiWallet


@api_view(["GET"])
@permission_classes([AllowAny])
def get_user_wallet(request):
    wallet = UserWallet.objects.filter(user=request.data.get("user_id")).first()
    if not wallet:
        return Response({"success": False, "message": "Wallet not found"}, status=404)

    transactions = [
        {
            "amount": float(tx.amount),
            "type": tx.transaction_type,
            "description": tx.description,
            "date": tx.timestamp 
        }
        for tx in wallet.transactions.order_by("-timestamp")
    ]

    return Response({
        "success": True,
        "balance": float(wallet.balance),
        "transactions": transactions
    })


@api_view(["GET"])
@permission_classes([AllowAny])
def get_saathi_wallet(request):
    saathi_profile = getattr(request.user, "saathi_profile", None)
    if not saathi_profile:
        return Response({"success": False, "message": "Saathi profile not found"}, status=404)

    wallet = SaathiWallet.objects.filter(saathi=saathi_profile).first()
    if not wallet:
        return Response({"success": False, "message": "Wallet not found"}, status=404)

    transactions = [
        {
            "amount": float(tx.amount),
            "type": tx.transaction_type,
            "description": tx.description,
            "date": tx.created_at
        }
        for tx in wallet.transactions.order_by("-created_at")
    ]

    return Response({
        "success": True,
        "balance": float(wallet.balance),
        "transactions": transactions
    })
