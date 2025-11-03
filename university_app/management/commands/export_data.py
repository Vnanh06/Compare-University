"""
Management command to export all data from SQL Server to JSON format
Usage: python manage.py export_data
"""
from django.core.management.base import BaseCommand
from django.core import serializers
from university_app.models import (
    Country, University, Major, Program, UniversityProgram,
    RankingSource, Ranking, Criteria, UniversityAdmissionRequirement
)
import json


class Command(BaseCommand):
    help = 'Export all database data to JSON files for migration to PostgreSQL'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting data export...'))

        # Export order matters (dependencies first)
        models_to_export = [
            ('countries', Country),
            ('ranking_sources', RankingSource),
            ('majors', Major),
            ('programs', Program),
            ('criteria', Criteria),
            ('universities', University),
            ('rankings', Ranking),
            ('university_programs', UniversityProgram),
            ('university_admission_requirements', UniversityAdmissionRequirement),
        ]

        all_data = []

        for model_name, model_class in models_to_export:
            self.stdout.write(f'Exporting {model_name}...')
            objects = model_class.objects.all()
            count = objects.count()

            if count > 0:
                # Serialize to JSON
                json_data = serializers.serialize('json', objects, indent=2)
                data = json.loads(json_data)
                all_data.extend(data)

                self.stdout.write(self.style.SUCCESS(f'  ✓ Exported {count} {model_name}'))
            else:
                self.stdout.write(self.style.WARNING(f'  ⚠ No data found for {model_name}'))

        # Save to file
        output_file = 'database_export.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_data, f, ensure_ascii=False, indent=2)

        self.stdout.write(self.style.SUCCESS(f'\n✓ Export complete! Saved to {output_file}'))
        self.stdout.write(self.style.SUCCESS(f'Total objects exported: {len(all_data)}'))

        self.stdout.write('\nTo import this data on Railway:')
        self.stdout.write('1. Upload database_export.json to your Railway project')
        self.stdout.write('2. Run: python manage.py loaddata database_export.json')
