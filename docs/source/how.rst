How it Works
============

Pytest gathers a list of test cases to be executed, by default it orders test cases from top to bottom of each file.  
This plugin takes that list and creates two sort keys.  The first is a sort key for each bucket, and the second is a sort key for each test.  
It then sorts the list of test cases using the two sort keys.

Bucket is simply a group of test cases.  Depending on the sitation it can be better to keep test cases grouped together.  
For example, if the test suite includes fixtures with a scope of module, it would be best to use a bucket type of module, class, or parent.  
This is becasue pytest will create that fixture every time testing eneters the module, and destroy it every time thesting leaves the module.

You can also separately control the sorting method for buckets and for test cases.  
For example, if you wanted to always run the modules in order provided by pytest, but wanted to randomize test order within each module.  
This can be achived by setting the Sort Mode to 'random', and the Bucket Sort Mode to 'ordered'.
