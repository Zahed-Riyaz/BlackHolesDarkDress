# pygadgetic
Create Gadget initial condition file with Python.





## Installation
   - Download the package or clone the repository
   - run the following command from the main pygadgetic directory

```sh
python setup.py install
```




## Requirements

   - numpy





## Cookbook

In order to produce an initial condition file using ***pygadgetic***, you need to follow the following steps:

   - put at the top of your script:

```python
import pygadgetic
```

   - create a header and a body object.
   - fill in the objects with your own code.
   - call dump_ic() function to produce the initial condition file (currently inly the binary type 1 format is supported).

You can also have a look at the example.py for an example of how to produce such a file.