set folder=t\sem

rm a.res

for %%i in (%folder%\*.in) do (
    python com.py %%i > %folder%\%%~ni.out
    )
)
