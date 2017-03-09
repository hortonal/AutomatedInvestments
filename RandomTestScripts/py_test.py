# -*- coding: utf-8 -*-
"""
Created on Mon Mar  6 19:03:08 2017

@author: Tom
"""


test = [1,2,3,4,5]
for y in filter(lambda x: x > 4, test):
    print(y)

    
el = next(filter(lambda x: x > 5, test), 2)

import matplotlib.pyplot as plt; plt.rcdefaults()
import numpy as np
import matplotlib.pyplot as plt
 
objects = ('Python', 'C++', 'Java', 'Perl', 'Scala', 'Lisp')
y_pos = np.arange(len(objects))
performance = [10,8,6,4,2,1]
 
plt.bar(y_pos, performance, align='center', alpha=0.5)
plt.xticks(y_pos, objects)
plt.ylabel('Usage')
plt.title('Programming language usage')
 
plt.show()