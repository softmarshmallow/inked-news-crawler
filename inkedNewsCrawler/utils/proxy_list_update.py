file_path = input("put list file location:: ")
data = open(file_path, 'r').read()
lines = data.split('\n')
for line in lines:
    items = line.split(' ')
    proxy = items[0]
    print(proxy)

