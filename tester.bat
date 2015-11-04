set folder=t\*

rm a.res
for /D %%j in (%folder%) do (
	echo %%j
	for %%i in (%%j\*.in) do (cp %%i input.txt
		python sol.py
		mv output.txt %%j\%%~ni.out
		fc %%j\%%~ni.ans %%j\%%~ni.out >> a.res 
		)
	)
