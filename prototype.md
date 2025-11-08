This document contains a bunch of ideas to better design the anatomy of this software

- Representing the ast in the most performant way possible for compilation purposes but also for editing purposes
    - The first option is to store it in a inverse-stack mode:
      ```
      // this is stored as a continous array=([]Node) where Node=(NodeKind, NodeHeaderIdx, ChildrenCount)
      // the NodeHeaderIdx is an index that points to a different array of different types based on NodeKind
      // for example the kind FunctionNode has the idx to point to the internal array of function_node_headers
      // and each element contains surface level information about that node, for example the number of arguments
      // the name of the function etc
      RootNode // all nodes below will be children of this
      FunctionNode 5 // all 5 nodes below will be children of this one
      
      ```
      For editing purposes, this will be diluted with empty spaces for each internal array, so there is no need to move all the nodes everytime one is inserted, but I still have O(1) access to each element