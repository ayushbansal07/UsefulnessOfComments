import sys

def main():
	if len(sys.argv) != 2:
		print "Error: Give exactly one input file"
		exit(-1)
	fname = sys.argv[1]
	f = open(fname, 'r')
	text = f.read()
	f.close()

	text = text.split("\n")
	out = []
	for each in text:
		now = each.replace(' ', '')
		if now.find("#include") == -1:
			out.append(each)
	ans = ""
	for each in out:
		ans += each + "\n"

	f = open(fname, 'wb')
	f.write(ans)
	f.close()
	
main()
