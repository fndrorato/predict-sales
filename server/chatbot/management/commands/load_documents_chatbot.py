import os
from django.core.management.base import BaseCommand
from items.models import Item, ItemGroupView, ItemControlStock
from sales.models import SalesGroupView
from stores.models import Store
from chatbot.utils import prepare_documents_from_queryset
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from langchain_community.embeddings import HuggingFaceEmbeddings

class Command(BaseCommand):
    help = 'Pré-processa dados para o Chatbot e armazena vetores em cache'

    def handle(self, *args, **kwargs):
        persist_dir = 'chatbot_db'
        embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        if not os.path.exists(persist_dir):
            os.makedirs(persist_dir)

        docs = []

        # 1. Dados das lojas
        docs += prepare_documents_from_queryset(
            Store.objects.all(), fields=['code', 'name']
        )

        # 2. Dados dos itens
        docs += prepare_documents_from_queryset(
            Item.objects.all(),
            fields=['code', 'name', 'cost_price', 'section', 'subsection', 'brand', 'sale_price']
        )

        # 3. Dados de controle de estoque com joins manuais
        item_stock_qs = ItemControlStock.objects.select_related("item", "store").all()
        for obj in item_stock_qs:
            content = (
                f"Item: {obj.item.name} (Código: {obj.item.code})\n"
                f"Loja: {obj.store.name} (Código: {obj.store.code})\n"
                f"Estoque disponível: {obj.stock_available}"
            )
            docs.append(Document(page_content=content))

        # 4. Grupos de item (view)
        docs += prepare_documents_from_queryset(
            ItemGroupView.objects.all(),
            fields=['id', 'name', 'section', 'subsection']
        )

        # 5. Agrupamento de vendas (view)
        docs += prepare_documents_from_queryset(
            SalesGroupView.objects.all(),
            fields=['item_group', 'store_id', 'date', 'total_quantity', 'total_revenue']
        )

        # Final: criar/atualizar vetor
        Chroma.from_documents(
            documents=docs,
            embedding=embedding_model,
            persist_directory=persist_dir,
        )

        self.stdout.write(self.style.SUCCESS('✅ Embeddings atualizados com sucesso.'))
