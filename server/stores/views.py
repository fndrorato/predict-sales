from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from stores.models import Store
from stores.serializers import StoreSerializer


class StoreListView(ListAPIView):
    queryset = Store.objects.all()
    serializer_class = StoreSerializer
    permission_classes = [IsAuthenticated]
