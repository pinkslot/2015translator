set folder=t

rm a.res
for /D %%j in (%folder%\lexer-*) do (
    echo %%j
    for %%i in (%%j\*.in) do (
        python com.py %%i > %%j\%%~ni.out l
        )
    )
