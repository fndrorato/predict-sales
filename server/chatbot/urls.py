from django.urls import path
from chatbot.views import ChatbotQueryView

urlpatterns = [
    path("chatbot/ask/", ChatbotQueryView.as_view(), name="chatbot-ask"),
]
