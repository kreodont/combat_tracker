# import singleton
# print(singleton.a)
# --------------------------- task ---------------
#Take all the items from second argument 'list' and add them to 'items' and then return concatenated list
# If second parameter is not specified, should return the unchanged first parameter
# ListsConcatenation(['a', 'b'], ['c', 'd']) = ['a', 'b', 'c', 'd']
# ListsConcatenation([1, 2, 3]) = [1, 2, 3]

# def ListsConcatenation(items, list=[]):
#     for l in list:
#     items[len(items)] = l
#     return items

# ------------------------- end of task -------------
# def ListsConcatenation(list1, list2=[]):
#     for l in list2:
#         list1.append(l)
#     return list1
# print(ListsConcatenation(['a', 'b'], ['c', 'd']))

#
# test_list1 = list_concatenation(['a', 'b'])
# print(test_list1)
# test_list2 = list_concatenation([1, 2, 3])
# print(test_list2)

# list1 = ['a', 'b']
# list2 = ['c', 'd']
# print(AddToList(list1, list2))

# string = 'd6'
# tokens = string.split('d')
# print(tokens)
# from dataclasses import dataclass, field
#
#
# @dataclass(frozen=True)
# class Value:
#     pass


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
