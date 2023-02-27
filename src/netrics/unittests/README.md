## Running Unittests
     
* * * * * * * * * * * * *

Author: Fathima Maha

### To run all tests:    

```
python3 -m unittest discover unittests -v
```       
    
### To run individual tests:   

```  
python3 -m unittest <test_filename> -v  
````       

### Unit test options:
    
-v - verbose      
-h - help   

## To get coverage:   
    
``` 
cd src
```
   
Get coverage of all tests for all files in builtin:   
```
pip install coverage    
coverage run --source=../builtin -m unittest discover -v && coverage report  
```      
Or 
```
coverage run --source=../builtin -m unittest discover -v && coverage report  
```
    
Get coverage of specific test for files in builtin:   
```
coverage run --source=../builtin <test_filename> -v -v && coverage report 
```     
   
### Reference:   

https://docs.python.org/3/library/unittest.html#unittest.main

https://coverage.readthedocs.io/en/7.1.0/