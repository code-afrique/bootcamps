#!/bin/awk -f
BEGIN {
	FS=",";
}
{
	{ print "\\cert{", $1, "}{", $2, "}" }
}
