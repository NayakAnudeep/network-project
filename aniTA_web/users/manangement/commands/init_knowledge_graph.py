# users/management/commands/init_knowledge_graph.py
from django.core.management.base import BaseCommand
from users.arango.graph_manager import safe_setup_knowledge_graph

class Command(BaseCommand):
    help = 'Initialize the AI TA knowledge graph in ArangoDB'

    def handle(self, *args, **options):
        self.stdout.write('Setting up AI TA knowledge graph...')
        
        success = safe_setup_knowledge_graph()
        
        if success:
            self.stdout.write(self.style.SUCCESS('Successfully initialized knowledge graph'))
        else:
            self.stderr.write(self.style.ERROR('Failed to initialize knowledge graph'))
