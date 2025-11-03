"""
Management command to rebuild ChromaDB vector database for chatbot
"""
from django.core.management.base import BaseCommand
from university_app.services.gemini_rag import GeminiChatbotRAG


class Command(BaseCommand):
    help = 'Rebuild ChromaDB vector database with all universities'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting ChromaDB rebuild...'))
        self.stdout.write('This may take 2-5 minutes depending on the number of universities.')
        self.stdout.write('')

        try:
            # Initialize chatbot and rebuild database
            chatbot = GeminiChatbotRAG()
            success = chatbot.rebuild_database()

            if success:
                # Get stats
                stats = chatbot.get_stats()

                self.stdout.write(self.style.SUCCESS('✓ ChromaDB rebuilt successfully!'))
                self.stdout.write('')
                self.stdout.write('Statistics:')
                self.stdout.write(f'  - Total universities indexed: {stats.get("total_documents", 0)}')
                self.stdout.write(f'  - Collection name: {stats.get("collection_name", "N/A")}')
                self.stdout.write(f'  - Embedding model: {stats.get("embedding_model", "N/A")}')
                self.stdout.write('')
                self.stdout.write('Chatbot is ready to use! 🤖')
            else:
                self.stdout.write(self.style.ERROR('✗ Failed to rebuild ChromaDB'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Error: {str(e)}'))
            raise
