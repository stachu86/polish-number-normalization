from unittest import TestCase
from polish_number_nomlizer import PolishNumberNormalizer


class TestPolishNumberNormalizer(TestCase):
    def test_numbers(self):
        normalizer = PolishNumberNormalizer()
        assert(normalizer("jeden")) == "1"
        assert normalizer("dwa") == "2"
        assert normalizer("dwadzieścia") == "20"
        assert normalizer("dwadzieścia trzy") == "23"
        assert normalizer("sto dwadzieścia trzy") == "123"
        assert normalizer("sto dwadzieścia trzy tysiące") == "123000"
        assert normalizer("sto dwadzieścia trzy miliony") == "123000000"
        assert normalizer("szesnaście tysięcy pięćset dwadzieścia dziewięć") == "16529"
        assert normalizer("sto milionów") == "100000000"
        assert normalizer("sto tysięcy dwieście trzynaście") == "100213"

    def test_telephone_numbers(self):
        normalizer = PolishNumberNormalizer()
        assert normalizer("jeden jeden dwa") == "112"
        assert normalizer("sto dwanaście") == "112"
        assert normalizer("zero siedemset sto trzy sto trzy pięćset") == "0700103103500"
        assert normalizer("sześć sześć sześć osiemset dwadzieścia trzy") == "66680023"
        assert normalizer("sześćset trzynaście") == "613"
        assert normalizer("plus czterdzieści osiem tysiąc dwanaście zero trzynaście sto") == "+481012013100"

    def test_negative_numbers(self):
        normalizer = PolishNumberNormalizer()
        assert normalizer("minus dwieście trzynaście") == "-213"
        assert normalizer("Jest minus dwieście trzynaście") == "jest -213"
        assert normalizer("minus jeden") == "-1"

    def test_dates(self):
        normalizer = PolishNumberNormalizer()
        assert normalizer("trzeci maja") == "3 maja"
        assert normalizer("pierwszy kwietnia") == "1 kwietnia"
        assert normalizer("trzydziesty pierwszy grudnia") == "31 grudnia"
        assert normalizer("trzydziestego pierwszego grudnia") == "31 grudnia"

    def test_times(self):
        normalizer = PolishNumberNormalizer()
        assert normalizer("O której odlatuje dzisiaj ten do Londynu jedenasta pięć?") == "o której odlatuje dzisiaj ten do londynu 11:05?"
        assert normalizer("Umówiłem się z nią o dwunastej") == "umówiłem się z nią o 12"
        assert normalizer("Pociąg odjeżddza siódma siedem") == "pociąg odjeżddza 7:07"
        assert normalizer("Pociąg odjeżddza szósta czterdzieści trzy") == "pociąg odjeżddza 6:43"


    def test_specials(self):
        normalizer = PolishNumberNormalizer()
        assert normalizer("dwa i pół") == "2,5"
        assert normalizer("siedem koma dwa") == "7,2"
        assert normalizer("sto procent") == "100%"
        assert normalizer("Tomek przyszedł jako jeden z pierwszych") == "tomek przyszedł jako 1 z pierwszych"

    def test_fractions(self):
        normalizer = PolishNumberNormalizer()
        assert normalizer("sześć dziesiątych") == "0,6"
        assert normalizer("trzy dziesiąte") == "0,3"
        assert normalizer("pięć dziesiątych") == "0,5"
        assert normalizer("dwadzieścia sześć setnych") == "0,26"
        assert normalizer("pięć tysięcznych") == "0,005"
        assert normalizer("jedna dziesiąta") == "0,1"
        assert normalizer("jeden i jedna setna") == "1,01"
        assert normalizer("piętnaście i czternaście tysięcznych") == "15,014"

    def test_exceptions(self):
        normalizer = PolishNumberNormalizer()
        assert normalizer("pięć.") == "5."
        assert normalizer("dwa, trzy.") == "2, 3."
        assert normalizer("sto!") == "100!"
        assert normalizer("sześć, sześć, sześć, osiemset dwadzieścia trzy") == "6, 6, 6, 823"
        assert normalizer("sześć, sześć, sześć, osiemset dwadzieścia, trzy") == "6, 6, 6, 820, 3"
        assert normalizer("sześć, sześć, sześć, osiemset, dwadzieścia, trzy") == "6, 6, 6, 800, 20, 3"

    def test_fire(self):
        normalizer = PolishNumberNormalizer()
        assert normalizer("Mieszka tam od tysiąc dziewięćset osiemdziesiątego drugiego") == "mieszka tam od 1982"
        assert normalizer("Mały Stasio ma dziś ósme urodziny!") == "mały stasio ma dziś 8 urodziny!"
        assert normalizer("Mały Stasio ma dziś dziesiąte urodziny!") == "mały stasio ma dziś 10 urodziny!"
        assert normalizer("Połączmy sie z adressem sto dziewięćdziesiąt dwa, sto sześćdziesiąt osiem, jeden, sto dwa.") == "połączmy sie z adressem 192, 168, 1, 102."

    def test_number_invariant(self):
        normalizer = PolishNumberNormalizer()
        assert normalizer("Urodził się w 1986.") == "urodził się w 1986."
        assert normalizer("Waży 90,5 kg.") == "waży 90,5 kg."
        assert normalizer("Waży 90.5 kg.") == "waży 90,5 kg."
        assert normalizer("Masz 100% racji!") == "masz 100% racji!"
