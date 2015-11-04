set /a j=63
setlocal ENABLEDELAYEDEXPANSION

for %%i in (*.in) do (
	mv %%i !j!.in
	set /a j=j+1
)
endlocal
