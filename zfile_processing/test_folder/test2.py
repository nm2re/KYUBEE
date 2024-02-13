# a = [5, 8, 13, 18]
# b = [8, 13, 19, 31]

a = [x for x in range(0, 25)]
b = [x for x in range(26, 50)]
a.sort()
c = []
i = 0
j = 0
k = 0
count = 0
while i < len(a) and j < len(b):
    if a[i] == b[j]:
        c.append(a[i])
        print(a[i])
        # c[k] = a[j]
        k += 1
        i += 1
        j += 1
        count += 1
    elif a[i] > b[j]:
        j += 1
        count += 1
    else:
        i += 1
        count += 1

print(c)
print(count)

div class="top-5 "

