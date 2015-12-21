set folder=t\parser-*

rm a.res
for /D %%j in (%folder%) do (
    for %%i in (%%j\*.in) do (
        python com.py %%i > %%j\%%~ni.out
        )
    )
