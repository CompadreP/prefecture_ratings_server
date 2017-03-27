from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import Group

from apps.employees.models import Organization
from apps.map.models import Region, District
from apps.ratings.models import BaseDocument, SignerText, RatingElement, \
    MonthlyRating, MonthlyRatingElement


class Command(BaseCommand):

    def handle(self, *args, **options):
        if Group.objects.count() > 0:
            raise CommandError("Groups already created!")
        if District.objects.count() > 0:
            raise CommandError("Districts already created!")
        if Region.objects.count() > 0:
            raise CommandError("Regions already created!")
        if Organization.objects.count() > 0:
            raise CommandError("Organization already created!")
        if BaseDocument.objects.count() > 0:
            raise CommandError("Base document already created!")
        if SignerText.objects.count() > 0:
            raise CommandError("Signer text already created!")
        if RatingElement.objects.count() > 0:
            raise CommandError("Rating elements already created!")
        if MonthlyRating.objects.count() > 0:
            raise CommandError("Monthly rating already created!")
        if MonthlyRatingElement.objects.count() > 0:
            raise CommandError("Monthly rating elements already created!")
        Group.objects.create(name='prefecture')
        Group.objects.create(name='regions')
        district = District.objects.create(name='САО')
        Region.objects.create(
            district=district,
            name='Аэропорт'
        )
        Region.objects.create(
            district=district,
            name='Беговой'
        )
        Region.objects.create(
            district=district,
            name='Бескудниковский'
        )
        Region.objects.create(
            district=district,
            name='Войковский'
        )
        Region.objects.create(
            district=district,
            name='Восточное Дегунино'
        )
        Region.objects.create(
            district=district,
            name='Головинский'
        )
        Region.objects.create(
            district=district,
            name='Дмитровский'
        )
        Region.objects.create(
            district=district,
            name='Западное Дегунино'
        )
        Region.objects.create(
            district=district,
            name='Коптево'
        )
        Region.objects.create(
            district=district,
            name='Левобережный'
        )
        Region.objects.create(
            district=district,
            name='Молжаниновский'
        )
        Region.objects.create(
            district=district,
            name='Савёловский'
        )
        Region.objects.create(
            district=district,
            name='Сокол'
        )
        Region.objects.create(
            district=district,
            name='Тимирязевский'
        )
        Region.objects.create(
            district=district,
            name='Ховрино'
        )
        Region.objects.create(
            district=district,
            name='Хорошёвский'
        )
        Organization.objects.create(
            name='Префектура САО',
            district=district
        )
        base_document = BaseDocument.objects.create(
            kind=1,
            description='Распоряжение префектуры САО от 08.09.2016 №532',
            description_imp='распоряжением префектуры САО от 08.09.2016 №532'
        )
        signer_text = SignerText.objects.create(
            text='УТВЕРЖДАЮ\nПервый заместитель префекта\nСеверного административного округа\nгорода Москвы\n\n___________________А.А.Велиховский',
            is_active=True
        )
        RatingElement.objects.create(
            number=1,
            base_document=base_document,
            name='Результаты работы района по данным ОАТИ города Москвы.',
            base_description='Показатель формируется на основании еженедельных отчетов ОАТИ по количеству выявленных нарушений (зеленой инспекции, инспекции по благоустройству).',
            weight=10,
            valid_from_month=1,
            valid_from_year=2016,
        )
        RatingElement.objects.create(
            number=2,
            base_document=base_document,
            name='Результаты работы района по данным Мосжилинспекции.',
            base_description='На основании еженедельных отчетов ЖИ по САО указывается процент выявленных нарушений (количество МКД с нарушениями/общее количество МКД в районе).',
            weight=10,
            valid_from_month=1,
            valid_from_year=2016,
        )
        RatingElement.objects.create(
            number=3,
            base_document=base_document,
            name='Исполнительская дисциплина.',
            base_description='Показатель формируется на основании ежемесячного отчета по возвращенным на доработку документам в управы районов в Системе ЭДО.',
            weight=10,
            valid_from_month=1,
            valid_from_year=2016,
        )
        RatingElement.objects.create(
            number=4,
            base_document=base_document,
            name='Телеметрический контроль за работой коммунальной техники.',
            base_description='Отчет о посещении коммунально-уборочной техникой площади проезжей части, тротуаров ОДХ и ДТ и выполнение технологических операций в соответствии с факсограммами КГХ по данным портала monitor.mos.ru.',
            weight=10,
            valid_from_month=1,
            valid_from_year=2016,
        )
        RatingElement.objects.create(
            number=5,
            base_document=base_document,
            name='Санитарное и техническое состояние коммунальной техники и средств малой механизации ГБУ "Жилищник" районов.',
            base_description='Количество техники находящейся в ремонте, не пройденного ТО и ГТО на основании проверок и информации представляемой ГБУ "Доринвест".',
            weight=10,
            valid_from_month=1,
            valid_from_year=2016,
        )
        RatingElement.objects.create(
            number=6,
            base_document=base_document,
            name='Ремонт подъездов.',
            base_description='Показатель формируется по еженедельным отчетам МЖИ по различным показателям.',
            weight=10,
            valid_from_month=1,
            valid_from_year=2016,
        )
        RatingElement.objects.create(
            number=7,
            base_document=base_document,
            name='Выполнение программы благоустройства дворовых и иных территорий.',
            base_description='Внесение данных по программам благоустройства в ИАС МКР.',
            weight=1,
            valid_from_month=1,
            valid_from_year=2016,
        )
        RatingElement.objects.create(
            number=8,
            base_document=base_document,
            name='Подготовка  жилого фонда и прочих строений к эксплуатации в зимних\летних условиях.',
            base_description='Подготовка жилого фонда и прочих строений к ОЗП.',
            weight=10,
            valid_from_month=2,
            valid_from_year=2017,
        )
        RatingElement.objects.create(
            number=9,
            base_document=base_document,
            name='Работа с бытовыми, крупногабаритными отходами и БРТС.',
            base_description='Показатели формируются на основании предоставляемых актов по обследованию БРТС за отчетный период, подтверждающих представляемые ранее сведения о проводимой с БРТС работе.',
            weight=10,
            valid_from_month=1,
            valid_from_year=2016,
        )
        RatingElement.objects.create(
            number=10,
            base_document=base_document,
            name='Выполнение региональной программы капитального ремонта.',
            base_description='Снижение балла основывается на количестве МКД и нежилых объектов в районе, взнос оплаты по которым не выполнен на 100%. Снижение балла основывается на количестве исходно-разрешительной документации (ИРД) по району, количество сдачи которых не выполнено на 100%.',
            weight=10,
            valid_from_month=1,
            valid_from_year=2016,
        )
        RatingElement.objects.create(
            number=11,
            base_document=base_document,
            name='Работа с кадрами ГБУ "Жилищник" районов, включая показатель набора численности по данным АИС «Бюджетный учет».',
            base_description='Показатель формируется по данным из аналитического портала Облачной бухгалтерии.',
            weight=10,
            valid_from_month=1,
            valid_from_year=2016,
        )
        RatingElement.objects.create(
            number=12,
            base_document=base_document,
            name='Задолженность населения и валовый сбор платежей за коммунальные услуги.',
            base_description='Показатель формируется по еженедельным отчетам ГКУ "Дирекция ЖКХиБ САО" в рамках подготовки к тепловой комиссии на основании базы АСУ ЕИРЦ.',
            weight=10,
            valid_from_month=1,
            valid_from_year=2016,
        )
        RatingElement.objects.create(
            number=13,
            base_document=base_document,
            name='Задолженность управляющих, эксплуатирующих и подведомственных организаций перед поставщиками услуг и ресурсов.',
            base_description='Данный показатель взят на основании еженедельных отчетов АО "Мосводоканал", АО "Мосгаз", ПАО "Мосэнергосбыт", ПАО МОЭК и лифтовых компаний и формируется отдельно по ГБУ и частным УО.',
            weight=10,
            valid_from_month=1,
            valid_from_year=2016,
        )
        RatingElement.objects.create(
            number=14,
            base_document=base_document,
            name='Санитарное и техническое состояние жилых домов, административных зданий и сооружений (инженерные системы МКД, работа ОДС, лифтовое оборудование и другие системы).',
            base_description='Исходные данные для расчета рейтинга, в части работы ОДС и представления отчетов по неисправностям  лифтового оборудования и очистке кровель, основываются на:\n1) Своевременном представлении отчетов (согласно факсограмме №6-7-139/7, № 6-7-5125/6, 6-7-310/7, 6-7-274/7;\n2) Проверок ОДС;\n3) Представлении районами необходимых материалов устранения нарушений, выявленных при проверке ОДС.',
            weight=10,
            valid_from_month=1,
            valid_from_year=2016,
        )
        RatingElement.objects.create(
            number=15,
            base_document=base_document,
            name='Проведение общих собраний собственников помещений МКД и качество оформления протоколов, а также проведения конкурсов по выбору управляющих организаций.',
            base_description='Проведение собраний с жителями жилых домов в районах округа.',
            weight=10,
            valid_from_month=1,
            valid_from_year=2016,
        )
        RatingElement.objects.create(
            number=16,
            base_document=base_document,
            name='Санитарное и техническое состояние территории округа и объектов инфраструктуры.',
            base_description='Показатель формируется на основании еженедельных отчетов СМЦ САО.',
            weight=10,
            valid_from_month=1,
            valid_from_year=2016,
        )
        RatingElement.objects.create(
            number=17,
            base_document=base_document,
            name='Санитарное и техническое состояние бытовых городков и баз хранения, а также других строений и территорий, находящихся на балансе ГБУ "Жилищник" районов.',
            weight=10,
            valid_from_month=2,
            valid_from_year=2017,
        )
        rating = MonthlyRating.objects.create(
            base_document=base_document,
            is_negotiated=False,
            is_approved=False,
            year=2017,
            month=2,
            signer_text=signer_text
        )
        for element in RatingElement.objects.all():
            MonthlyRatingElement.objects.create(
                monthly_rating=rating,
                rating_element=element
            )
        print('Success!')
