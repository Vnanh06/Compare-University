"""
Management command to create all database tables manually
Since models have managed=False, Django won't create them automatically
"""
from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = 'Create all database tables (for managed=False models)'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Creating database tables...'))

        with connection.cursor() as cursor:
            # Create countries table
            self.stdout.write('Creating countries table...')
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS countries (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255) NOT NULL
                );
            """)

            # Create ranking_sources table
            self.stdout.write('Creating ranking_sources table...')
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ranking_sources (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    description TEXT
                );
            """)

            # Create majors table
            self.stdout.write('Creating majors table...')
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS majors (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255) NOT NULL
                );
            """)

            # Create programs table
            self.stdout.write('Creating programs table...')
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS programs (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    level VARCHAR(255)
                );
            """)

            # Create criteria table
            self.stdout.write('Creating criteria table...')
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS criteria (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    unit VARCHAR(255),
                    description TEXT
                );
            """)

            # Create universities table
            self.stdout.write('Creating universities table...')
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS universities (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    short_name VARCHAR(255),
                    country_id INTEGER REFERENCES countries(id) ON DELETE CASCADE,
                    founded_year INTEGER,
                    website VARCHAR(255),
                    description TEXT
                );
            """)

            # Create rankings table
            self.stdout.write('Creating rankings table...')
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS rankings (
                    id SERIAL PRIMARY KEY,
                    university_id INTEGER REFERENCES universities(id) ON DELETE CASCADE,
                    ranking_sources_id INTEGER REFERENCES ranking_sources(id) ON DELETE CASCADE,
                    fyear INTEGER,
                    frank INTEGER
                );
            """)

            # Create university_programs table
            self.stdout.write('Creating university_programs table...')
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS university_programs (
                    id SERIAL PRIMARY KEY,
                    university_id INTEGER REFERENCES universities(id) ON DELETE CASCADE,
                    program_id INTEGER REFERENCES programs(id) ON DELETE CASCADE,
                    major_id INTEGER REFERENCES majors(id) ON DELETE CASCADE,
                    tuition_fee DOUBLE PRECISION,
                    duration VARCHAR(255)
                );
            """)

            # Create university_admission_requirements table
            self.stdout.write('Creating university_admission_requirements table...')
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS university_admission_requirements (
                    id SERIAL PRIMARY KEY,
                    university_id INTEGER REFERENCES universities(id) ON DELETE CASCADE,
                    criteria_id INTEGER REFERENCES criteria(id) ON DELETE CASCADE,
                    program_id INTEGER REFERENCES programs(id) ON DELETE CASCADE,
                    value VARCHAR(255)
                );
            """)

            # Create indexes for better performance
            self.stdout.write('Creating indexes...')
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_universities_country ON universities(country_id);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_rankings_university ON rankings(university_id);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_rankings_source ON rankings(ranking_sources_id);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_university_programs_university ON university_programs(university_id);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_university_programs_major ON university_programs(major_id);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_admission_reqs_university ON university_admission_requirements(university_id);")

        self.stdout.write(self.style.SUCCESS('✓ All tables created successfully!'))
        self.stdout.write('')
        self.stdout.write('Next steps:')
        self.stdout.write('1. Run: railway run python manage.py loaddata database_export.json')
        self.stdout.write('2. Run: railway run python manage.py createsuperuser')
