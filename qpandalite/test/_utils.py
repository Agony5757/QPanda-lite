def qpandalite_test(testname):
    def decorator(func):
        def wrapper(*args, **kwargs):
            print(f"-------------- Test {testname} --------------")
            result = func(*args, **kwargs)
            print(f"------------ Test {testname} OK -------------")
            return result
        return wrapper
    return decorator