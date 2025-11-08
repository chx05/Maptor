A bunch of ideas related to the editor

- Try data structures out without launching the program, meaning I can design data more easily by instantiating stuff in the editor and visualizing it in order to spot better ways to organize data
- With the same visualization tools to try data structures directly in the editor, I also want to visualize data at runtime when debugging
- Custom data structures can attach some editor script to visualize the data structure in a custom way, so I can visualize a hand written tree with nodes and links, directly in the editor, when debugging or when trying structures out directly in the editor
- With the same logic, I may implement a custom versioning system that works with ast nodes instead of text characters, the visualization of the repository should also happen directly in the editor, in a dedicated map
- As well as a integrated interactive terminal, I should be able to use the language itself as scripting language instead of bash/batch
- All the code that runs at compile time or interacts with the editor (pseudo compile time) will be interpreted, and it will always be all in the custom language itself
- Functions, methods, structs etc should be pickable from a side menu (sorted alphabetically), no concept of multiple files, just all symbols merged toghether, maybe divided in different subgroups to delimit their usespace (instead of namespace)
- Functions, methods, structs etc should be visualized on the map optionally and in a "blocky" shape, meaning I can actually move them around, althought the editor will help me aligning the blocks
- There should be no concept of long scrolling text as it happens in files, this editor uses a map view, not a file view, you can have functions placed in parallel along the X axis instead of the Y axis
