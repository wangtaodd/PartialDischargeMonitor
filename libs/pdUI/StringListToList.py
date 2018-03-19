
str_lst = '[1, 2, 3]'
str = str_lst.strip('[]').split(',')
int_lst = [int(x) for x in str]

print (int_lst)
