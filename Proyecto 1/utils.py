def log(t,file):
    file = open(file,'a')
    print(t,end="")
    file.write(t)
    file.close()
