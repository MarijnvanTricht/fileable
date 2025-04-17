# fileable

simple way to save and load python classes with a few fallbacks

## example usage

```python
file = Fileable()
file.stuff = "stuff to save"
file.lst = ["to", "save"]
file.thisdict = { "brand": "Ford", "model": "Mustang" }
file.saveToFile("test.file")
```

Then

```python
file = Fileable.loadFromFile("test.file")
print(file.stuff)
print(file.lst)
print(file.thisdict)
```

Will output

```
stuff to save
['to', 'save']
{'brand': 'Ford', 'model': 'Mustang'}
```