xpaths = ['/html/body/form/div/div/div[2]/div[2]/div[3]/div[2]/div[1]/div/div/div[2]/h1/a',
'/html/body/form/div/div/div[2]/div[2]/div[3]/div[5]/div[1]/div/div/div[2]/h1/a']
print(xpaths[0].split('/'))
print(xpaths[1].split('/'))
xpaths[0] = xpaths[0].split('/')
xpaths[1] = xpaths[1].split('/')

var_index = 0
for index, path in enumerate(xpaths[0]):
    if path != xpaths[1][index]:
        var_index = index
print(var_index)