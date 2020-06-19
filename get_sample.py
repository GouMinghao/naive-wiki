fr = open('pages.xml','rb')
fw = open('pages_sample_big.xml','wb')
total_size = 76927677600
sample_size = total_size / 20
for i in range(100):
    print('\r%02d%%' %(i+1,),end='')
    data = fr.read(int(sample_size / 100))
    fw.write(data)
print('')
print('Done!')
fr.close()
fw.close()
    