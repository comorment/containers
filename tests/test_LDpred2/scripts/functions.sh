### Just some function to simplify testing output codes
### Note that warnings are not captured

function echoRed () {
	echo -e "\033[0;31m$1\033[0m"
}
# These functions will spit out command output when exit code departs from the expected
# Arg 1: Expected exit code (0 - no error, 1 error)
# Arg 2: The command to execute as a string
function testCommand () {
	dump=$( { ${@:2} ; } 2>&1 )
	err=$?
	if [ ! $err -eq $1 ]; then 
		echoRed "ERROR ===>"
		echo "$dump"
		echoRed "<=== END ERROR"
	fi
}
# Test successful command
function testSuccess () {
	testCommand 0 $@
}
# Test failing command
function testException () {
	testCommand 1 $@
}
