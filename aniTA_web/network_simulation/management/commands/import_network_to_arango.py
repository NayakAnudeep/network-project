from django.core.management.base import BaseCommand
from network_simulation.import_to_arango import import_network_to_arango
import os

class Command(BaseCommand):
    help = 'Import network simulation data to ArangoDB'

    def add_arguments(self, parser):
        parser.add_argument('--json', type=str, default='network_data.json',
                            help='Path to network data JSON file')
        parser.add_argument('--csv-dir', type=str, default='csv_data',
                            help='Directory containing credential CSV files')

    def handle(self, *args, **options):
        json_file = options['json']
        csv_dir = options['csv_dir']
        
        # Resolve paths - if not absolute, assume relative to the current directory
        if not os.path.isabs(json_file):
            json_file = os.path.join(os.getcwd(), json_file)
        
        if not os.path.isabs(csv_dir):
            csv_dir = os.path.join(os.getcwd(), csv_dir)
        
        self.stdout.write(self.style.SUCCESS(f'Importing network data from {json_file} to ArangoDB...'))
        
        if not os.path.exists(json_file):
            self.stdout.write(self.style.ERROR(f'File not found: {json_file}'))
            return
            
        if not os.path.exists(csv_dir):
            self.stdout.write(self.style.WARNING(f'CSV directory not found: {csv_dir}. Will skip user credentials.'))
        
        try:
            result = import_network_to_arango(json_file, csv_dir)
            
            self.stdout.write(self.style.SUCCESS('Import completed!'))
            for entity, count in result.items():
                self.stdout.write(f'  - {entity}: {count}')
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error importing data: {str(e)}'))