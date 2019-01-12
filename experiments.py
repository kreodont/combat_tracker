# import singleton
# print(singleton.a)
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Value:
    pass


# import datetime
# import pickle
# class A:
#     pass

# tuple_ = (1, 2)
# list_ = [1, 2]
# another_dict = {}
# a = A()
# a.b = [3, ]
# dict_ = {a: 1, datetime.datetime.now(): 4}
#
# print(dict_)
# string = pickle.dumps(dict_)
# print(string)
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
