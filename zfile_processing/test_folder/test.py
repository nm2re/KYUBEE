a = input()
set_a = input()
set_a=set(set_a)
b = input()
set_b = input()
set_b = set(set_b)

print(set_a)
print(set_b)

# set_a.difference(set_b)
set_a = {element for element in set_a if element.isdigit()}
set_b = {element for element in set_b if element.isdigit()}
set_a = set(map(int, set_a))
set_b = set(map(int, set_b))

print(set_a)
print(set_b)
ans = set_a.difference(set_b)
print(ans)
