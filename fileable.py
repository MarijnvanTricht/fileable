"""
fileable.py

Author: Marijn van Tricht
Date: 2025-04-17
Description:
    Yet another incomplete way to save and load python classes
"""
import builtins
import inspect
import sys
import ast

class Fileable:
    class Utilities:
        @staticmethod 
        def isIterable(obj):
            try:
                iter(obj)
                return not isinstance(obj, (str, bytes, dict))
            except TypeError:
                return False
            
        @staticmethod 
        def serializeType(value):
            className = type(value).__name__.encode('utf-8')
            return len(className).to_bytes(4, 'big') + className

        @staticmethod 
        def serializeValue(value):
            inputValue = str(value).encode('utf-8')
            return len(inputValue).to_bytes(4, 'big') + inputValue

        @staticmethod 
        def deserializeValue(data, index):
            length = int.from_bytes(data[index:index+4], 'big')
            value = data[index+4:index+4+length].decode('utf-8')
            return value, index + 4 + length

        @staticmethod
        def deserializeType(data, index):
            value, index = Fileable.Utilities.deserializeValue(data, index)
            cls_type = Fileable.Utilities.resolveClassName(value)
            return cls_type, index

        @staticmethod
        def resolveClassName(name, max_depth=10):
            frame = sys._getframe()

            for _ in range(max_depth):
                if name in frame.f_locals:
                    return frame.f_locals[name]
                if name in frame.f_globals:
                    return frame.f_globals[name]
                frame = frame.f_back
                if frame is None:
                    break

            if name in dir(builtins):
                a = getattr(builtins, name)
                if inspect.isclass(a):
                    return a

            raise ValueError(f"Class name not recognized: {name}")

    def serialize(self):
        data = b''
        if Fileable.Utilities.isIterable(self):
            data += len(self).to_bytes(4, 'big')
            for item in self:
                newData = b''
                newData += Fileable.Utilities.serializeType(item)
                if hasattr(item, "serialize"):
                    newData += item.serialize()
                else:
                    newData += Fileable.Utilities.serializeValue(item)
                data += len(newData).to_bytes(4, 'big') + newData

        attributes = self.__dict__.items()
        data += len(attributes).to_bytes(4, 'big')
        for attr, value in attributes:
            newData = b''
            newData += Fileable.Utilities.serializeType(value)
            newData += Fileable.Utilities.serializeValue(attr)
            if hasattr(value, "serialize"):
                newData += value.serialize()
            else:
                newData += Fileable.Utilities.serializeValue(value)

            data += len(newData).to_bytes(4, 'big') + newData

        return data

    def deserialize(self, data, index):
        beginIndex = index
        
        if Fileable.Utilities.isIterable(self):
            length = int.from_bytes(data[index:index+4], 'big')
            index += 4
            for _ in range(length):
                objLength = int.from_bytes(data[index:index+4], 'big')
                index += 4
                thisIndex = index
                try:
                    newObj, index = Fileable.Utilities.deserializeType(data, index)
                    
                    if hasattr(newObj, "deserialize"):
                        newObj = newObj.__new__(newObj)
                        _, index = newObj.deserialize(data, index)
                    else:
                        objdata, index = Fileable.Utilities.deserializeValue(data, index)
                        newObj = newObj(objdata)

                    self.append(newObj)
                    
                except ValueError as e:
                    print("Warning " + str(e) + ", skipping.. ")
                    index = thisIndex + objLength                   

        length = int.from_bytes(data[index:index+4], 'big')
        index += 4
        for _ in range(length):
            objLength = int.from_bytes(data[index:index+4], 'big')
            index += 4
            thisIndex = index
            try:
                newObj, index = Fileable.Utilities.deserializeType(data, index)
                name, index = Fileable.Utilities.deserializeValue(data, index)
                
                if hasattr(newObj, "deserialize"):
                    newObj = newObj.__new__(newObj)
                    _, index = newObj.deserialize(data, index)
                else:
                    objdata, index = Fileable.Utilities.deserializeValue(data, index)
                    try:
                        objdata = ast.literal_eval(objdata)
                    except:
                        pass
                    newObj = newObj(objdata)

                setattr(self, name, newObj)

            except ValueError as e:
                print("Warning " + str(e) + ", skipping.. ")
                index = thisIndex + objLength

        return data, index
    
    def saveToFile(self, filename):
        data = b''
        data += Fileable.Utilities.serializeType(self)
        data += self.serialize()
        with open(filename, 'wb') as f:
            f.write(data)

    @classmethod
    def loadFromFile(cls, filename):
        data = None
        index = 0
        with open(filename, 'rb') as f:
            data = f.read()
        newClass, index = cls.Utilities.deserializeType(data, index)
        newObj = newClass()
        data, index = newObj.deserialize(data, index)
        return newObj

if __name__ == "__main__":

    file = Fileable()
    file.stuff = "stuff to save"
    file.lst = ["to", "save"]
    file.thisdict = { "brand": "Ford", "model": "Mustang" }

    file.saveToFile("test.file")
    
    print(file.stuff)
    print(file.lst)
    print(file.thisdict)    
    
    file = Fileable.loadFromFile("test.file")
    print(file.stuff)
    print(file.lst)
    print(file.thisdict)
    
    
