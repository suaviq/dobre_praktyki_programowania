import pytest 
from functions import is_palindrome

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