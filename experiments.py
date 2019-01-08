import singleton
print(singleton.a)
# class A:
#     pass
#
# tuple_ = (1, 2)
# list_ = [1, 2]
# another_dict = {}
# a = A()
# dict_ = {a: 1, tuple_: 2, another_dict: 4}
# print(dict_)
# import time
#
#
# def timeit(decorator_parameter):
#     def parameter(f):
#         def wrapper(*args, **kwargs):
#             start = time.time()
#             result = f(*args, **kwargs)
#             end = time.time()
#             print(round(end - start, decorator_parameter))
#             return result
#         return wrapper
#     return parameter
#
#
# @timeit(3)
# def wait_for_3_seconds():
#     time.sleep(3)
#
#
# wait_for_3_seconds()
