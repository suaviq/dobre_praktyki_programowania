import pytest 
from functions import is_palindrome, fibonacci

class TestIsPalindrome:
    def test_kajak(self):
        assert is_palindrome("kajak") == True
    
    def test_kobyla_ma_maly_bok(self):
        assert is_palindrome("Kobyla ma mały bok") == True
    
    def test_python(self):
        assert is_palindrome("python") == False
    
    def test_empty_string(self):
        assert is_palindrome("") == True
    
    def test_single_character(self):
        assert is_palindrome("A") == True

class TestFibonacci:
    def test_fibonacci_0(self):
        assert fibonacci(0) == 0
    
    def test_fibonacci_1(self):
        assert fibonacci(1) == 1
    
    def test_fibonacci_5(self):
        assert fibonacci(5) == 5
    
    def test_fibonacci_10(self):
        assert fibonacci(10) == 55
    
    def test_fibonacci_negative(self):
        with pytest.raises(ValueError):
            fibonacci(-1)