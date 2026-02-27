from chatbot.models import ChatbotLog
from chatbot.utils import ask_question_with_sql_agent
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated


class ChatbotQueryView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        question = request.data.get("question")
        if not question:
            return Response({"error": "Pergunta ausente."}, status=400)

        # Identificador único para a sessão do usuário
        session_id = str(request.user.id)

        answer = ask_question_with_sql_agent(question, session_id)

        ChatbotLog.objects.create(
            user=request.user,
            question=question,
            answer=answer,
        )

        return Response({"answer": answer})



