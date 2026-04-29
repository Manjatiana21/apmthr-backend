from django.shortcuts import render

# Create your views here.
from rest_framework.generics import ListAPIView
from .models import Facture
from .serializers import FactureSerializer

class FactureListAPIView(ListAPIView):
    queryset = Facture.objects.all().order_by("-date_emission")
    serializer_class = FactureSerializer
