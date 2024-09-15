l = ['ali', 'jafar', 'mmd']
ali_index = l.index("mmd")
l.remove("mmd")
l.insert(ali_index, "SOMEONE")
print(l)