import datetime
from faker import Faker
from factory import fuzzy, List,  SubFactory, DictFactory
fake = Faker('nl_NL')


class PGBFactory(DictFactory):
    Jaar = 2018
    Ingangsdatum = fuzzy.FuzzyDate(datetime.date(2008, 1, 1)).__str__()
    Einddatum = fuzzy.FuzzyDate(datetime.date(2008, 1, 1)).__str__()
    Bedrag = fuzzy.FuzzyDecimal(100, 1000, 2)


class VoorzieningFactory(DictFactory):
    omschrijving = fake.sentence()  # pylint: disable=no-member
    Wet = fuzzy.FuzzyInteger(0, 3)
    Actueel = fuzzy.FuzzyChoice([True, False])
    Startdatum = fuzzy.FuzzyDate(datetime.date(2008, 1, 1)).__str__()
    Einddatum = fuzzy.FuzzyDate(datetime.date(2008, 1, 1)).__str__()
    Volume = fuzzy.FuzzyInteger(0, 100)
    Eenheid = fuzzy.FuzzyChoice(['01', '04', '14', '16', '82', '83'])
    Frequentie = fuzzy.FuzzyChoice([1, 2, 3, 4, 5, 6])
    Omvang = fake.name()  # pylint: disable=no-member
    Leverancier = fake.name()  # pylint: disable=no-member
    Checkdatum = fuzzy.FuzzyDate(datetime.date(2008, 1, 1)).__str__()
    PGBbudget = List([SubFactory(PGBFactory, year=year) for year
                      in [2016, 2017, 2018]])
