import csv
import os.path

from django.conf import settings
from django.core.management import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    help = "Loads data from ingredients.csv"

    def handle(self, *args, **options):

        # Если такие данные уже существуют
        # if Ingredient.objects.exists():
        #     print('Эти данные уже существуют')
        #     return

        # Показывать перед загрузкой данных
        print("Loading ingredients data")

        with open(os.path.join(settings.BASE_DIR / 'data/ingredients.csv'),
                  'r') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            for row in csv_reader:
                Ingredient.objects.get_or_create(name=row[0],
                                                 measurement_unit=row[1])

        self.stdout.write("The ingredients has been loaded successfully.")
