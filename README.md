# DecodeDemcon3 Challence Solution Description

To run, simply run the script mineSweeper.py.
The solution applied in the script is explained at the top of the script.
To change parameters in execution, simply change the parameters width, height, and mines_left in the script.

If the solution is found, it is printed as such on the screen.

Please note that the recursive algorithm applied can always find the perfect solution, if it exists.
The downside is that it can be very slow. Therefore, a limit is set on the recursion depth, making it near perfect.
If it seems to hang, please give it a few seconds! If it keeps hanging, then it is possible to reduce the MAX_RECURSION_DEPTH parameter.
