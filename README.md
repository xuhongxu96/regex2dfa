# regex2dfa
DFA Generator From Simple Regular Expression (including '*' '|' '(' ')')

## Examples

The example code is in the main python file.
Following is the output.

```
1(1010*|1(010)*1)*0
('.', ('v', '1'), ('.', ('*', ('|', ('.', ('v', '1'), ('.', ('v', '0'), ('.', ('v', '1'), ('*', ('v', '0'))))), ('.', ('v', '1'), ('.', ('*', ('.', ('v', '0'), ('.', ('v', '1'), ('v', '0')))), ('v', '1'))))), ('v', '0')))
----
1(0|1)*101
('.', ('v', '1'), ('.', ('*', ('|', ('v', '0'), ('v', '1'))), ('.', ('v', '1'), ('.', ('v', '0'), ('v', '1')))))
```

![img1](https://raw.githubusercontent.com/xuhongxu96/regex2dfa/master/img1.png)
![img2](https://raw.githubusercontent.com/xuhongxu96/regex2dfa/master/img2.png)
