from functools import wraps

def test(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        print(f"▶ Running {func.__name__}...")
        try:
            result = func(*args, **kwargs)
            print(f"✅ {func.__name__} passed.\n")
            return result
        except Exception as e:
            print(f"❌ {func.__name__} failed: {e}\n")
            raise
    return wrapper