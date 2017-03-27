from typing import Dict

from openpyxl import Workbook

from apps.map.models import Region
from apps.ratings.models import MONTHS, MonthlyRating


class MonthlyRatingExcelGenerator:

    def __init__(self, monthly_rating: MonthlyRating):
        self.monthly_rating = monthly_rating
        self.regions = Region.objects.all()
        self.wb = Workbook()

    def save(self):
        self.generate_main_sheet()
        self.wb.save(
            'Месячный_рейтинг_{}_{}.xlsx'.format(
                self.monthly_rating.year,
                self.monthly_rating.month,
            )
        )

    def get_sum_values(self) -> Dict:
        sum_values = {}
        for region in self.regions:
            sum_values[region.id] = 0
        return sum_values

    def get_max_possible_value(self) -> int:
        max_sum = 0
        for element in self.monthly_rating.elements:
            max_sum += element.rating_element.weight
        return max_sum

    def generate_main_sheet(self) -> None:
        main_ws = self.wb.create_sheet(MONTHS[self.monthly_rating.month])
        main_ws.column_dimensions['A'].width = 270
        main_ws.column_dimensions['B'].width = 110
        for col in ['C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N',
                    'O', 'P', 'Q', 'R']:
            main_ws.column_dimensions[col].width = 40

        main_ws.column_dimensions['S'].width = 60
        main_ws.column_dimensions['T'].width = 520
        main_ws.column_dimensions['U'].width = 170
        main_ws.column_dimensions['V'].width = 130

        main_ws['T1'] = self.monthly_rating.signer_text.text
        main_ws['A2'] = \
            'Исходные данные для расчета рейтинга управ районов САО ' \
            'в части показателей ЖКХ за {month} {year} года в соответствии с ' \
            '{document}'.format(
                month=MONTHS[self.monthly_rating.month],
                year=self.monthly_rating.year,
                document=self.monthly_rating.base_document.description_imp
            )
        main_ws['A5'] = 'Наименование показателей'
        main_ws['A6'] = 'Суммарный показатель'
        main_ws['A7'] = 'Максимально возможный суммарный показатель'

        main_ws['B4'] = 'место'
        main_ws['B5'] = 'Ответственный'

        main_ws['S5'] = 'Средний'
        main_ws['T5'] = 'Описание показателя'
        main_ws['U5'] = 'Комментарии согласовывающего'
        main_ws['V5'] = 'Информация о замечаниях районов'

        sum_values = self.get_sum_values()

        for idx, region in enumerate(self.regions):
            main_ws.cell(row=5, column=idx + 3, value=region.name)
            main_ws.cell(row=6, column=idx + 3, value=sum_values[region.id])
            main_ws.cell(row=7, column=idx + 3, value=sum_values[region.id])

        for idx, element in enumerate(self.monthly_rating.elements.all()):
            main_ws.cell(
                row=idx + 9,
                column=1,
                value=element.rating_element.name
            )
            main_ws.cell(
                row=idx + 9,
                column=2,
                value=element.responsible.short_name if element.responsible else None
            )
            main_ws.cell(
                row=idx + 9,
                column=20,
                value=('{} {}'.format(
                    element.rating_element.base_description,
                    element.additional_description
                ))
            )
            main_ws.cell(
                row=idx + 9,
                column=21,
                value=(element.negotiator_comment)
            )
            main_ws.cell(
                row=idx + 9,
                column=22,
                value=(element.region_comment)
            )
