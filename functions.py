import string

def is_palindrome(text: str) -> bool:
    cleaned_text = text.replace(" ", "").lower()
    return cleaned_text == cleaned_text[::-1]


def fibonacci(n: int) -> int:
    if n < 0:
        raise ValueError("n must be non-negative")
    if n == 0:
        return 0
    elif n == 1:
        return 1
    
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b


def count_vowels(text: str) -> int:
    vowels = "aeiouyąęó"
    text_lower = text.lower()
    count = 0
    for char in text_lower:
        if char in vowels:
            count += 1
    return count


def calculate_discount(price: float, discount: float) -> float:
    if discount < 0 or discount > 1:
        raise ValueError("Discount must be between 0 and 1")
    
    return price * (1 - discount)


def flatten_list(nested_list: list) -> list:
    result = []
    
    def flatten(item):
        if isinstance(item, list):
            for subitem in item:
                flatten(subitem)
        else:
            result.append(item)
    
    flatten(nested_list)
    return result


def word_frequencies(text: str) -> dict:
    if not text.strip():
        return {}
    translator = str.maketrans('', '', string.punctuation)
    cleaned_text = text.translate(translator).lower()
    words = cleaned_text.split()
    frequency = {}
    
    for word in words:
        frequency[word] = frequency.get(word, 0) + 1
    
    return frequency


def is_prime(n: int) -> bool:
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    
    for i in range(3, int(n**0.5) + 1, 2):
        if n % i == 0:
            return False
    
    return True