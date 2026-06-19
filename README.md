The `PolishNumberNormalizer` class converts spelled-out numbers into their digit form.
In its current form, it supports integer numbers, decimal numbers with up to three digits of precision, and numerals used to express dates and time. To ensure unambiguous normalization of number sequences, individual numerals should be separated by commas.

The code is a modification of [`EnglishNumberNormalizer`](https://github.com/openai/whisper/blob/main/whisper/normalizers/english.py).
```python
normalizer = PolishNumberNormalizer()

# Numbers
assert(normalizer("jeden")) == "1"
assert normalizer("dwa") == "2"
assert normalizer("dwadzieścia") == "20"

# Telephone number
assert normalizer("plus czterdzieści osiem tysiąc dwanaście zero trzynaście sto") == "+481012013100"
assert normalizer("zero siedemset sto trzy sto trzy pięćset") == "0700103103500"

# Dates
assert normalizer("pierwszy kwietnia") == "1 kwietnia"
assert normalizer("trzydziesty pierwszy grudnia") == "31 grudnia"

# Decimal fractions
assert normalizer("dwadzieścia sześć setnych") == "0,26"
assert normalizer("jedna dziesiąta") == "0,1"
assert normalizer("jeden i jedna setna") == "1,01"

# Unambiguous number sequences
assert normalizer("sześć, sześć, sześć, osiemset dwadzieścia trzy") == "6, 6, 6, 823"
assert normalizer("sześć, sześć, sześć, osiemset dwadzieścia, trzy") == "6, 6, 6, 820, 3"
assert normalizer("sześć, sześć, sześć, osiemset, dwadzieścia, trzy") == "6, 6, 6, 800, 20, 3"
```
For more examples of expected behaviour check the [test cases](test_polish_number_normlizer.py).
