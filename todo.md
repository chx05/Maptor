* make backspace special actions: if we are in functioncall, backspacing on the open par should delete the call node, and related actions, merge this with the current string quoted lit elimination action
* switching should eliminate the exprbufnode in certain cases, for example in a function call `print()` should not become `print(_)` or `print(<hidden_empty_buf_ndoe>)`
* parallel mode should be local to individual nodes instead of being a global setting
* elimination of stmtbuf node should not happen when that bufnode is the last statement in the list, it should become a pass instead
* if-else chains should be a single node with an internal list, not a recursive node. search for a "TODO" in the codebase to find a precise point in which this is explained better