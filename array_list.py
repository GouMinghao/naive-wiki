import os
import numpy as np
class Array_List(object):
    def __init__(self,file_name):
        self.file_name = file_name
        if os.path.exists(file_name):
            self.from_file = True
            self.load_file()
        else:
            self.from_file = False
            self.data = np.array([],dtype = np.uint32)
            self.length = np.array([],dtype = np.uint32)
            self.offset = np.array([],dtype = np.uint32)
            self.current_offset = 0
        
    def get_array(self,idx):
        length = self.length[idx]
        offset = self.offset[idx]
        return self.data[offset:offset+length]
    
    def insert_array(self,arr):
        length = len(arr)
        self.offset = np.hstack((self.offset,np.array(self.current_offset)))
        self.length = np.hstack((self.length,np.array(length)))
        self.current_offset += length
        self.data = np.hstack((self.data,arr))

    def save_file(self):
        np.savez(self.file_name,data = self.data,length = self.length, offset = self.offset)

    def load_file(self):
        npz_file = np.load(self.file_name)
        self.data = npz_file['data']
        self.length = npz_file['length']
        self.offset = npz_file['offset']
        self.current_offset = self.length[-1] + self.offset[-1]

if __name__ == '__main__':
    a = Array_List('a.npz')
    if not a.from_file:
        b = np.array([1,2,3,4])
        c = np.array([3,4,5,6,7,8])
        a.insert_array(b)
        a.insert_array(c)

    print(a.get_array(0))
    print(a.get_array(1))
    a.save_file()