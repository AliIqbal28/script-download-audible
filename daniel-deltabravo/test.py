import os

filename_with_extension = os.listdir('audiobooks')[0]
filename, extension = filename_with_extension.split('.')
print(filename+'.json')