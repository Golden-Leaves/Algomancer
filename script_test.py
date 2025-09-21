def flatten_array(result,objs):
    if not isinstance(objs,(tuple,list)):
            result.append(objs)
            return result
    for obj in objs:
        flatten_array(result=result,objs=obj)
    return result

array = [[1,2,3],[2,3,4]]
print(flatten_array(result=[],objs=array))