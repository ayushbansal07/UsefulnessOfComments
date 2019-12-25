import os
import sys
import ntpath

INPUT_CODE = sys.argv[1]
FILE_NAME = INPUT_CODE[:INPUT_CODE.find(".")]
LINES_WITH_BUTTON = []
with open(FILE_NAME+".lines") as f:
	for line in f:
		line_nos = line.split(" ")
		for ln in line_nos:
			LINES_WITH_BUTTON.append(int(ln))

FILE_CODE_NAME = ntpath.basename(FILE_NAME)
output_lines = []
LAST_COMMENT = LINES_WITH_BUTTON[len(LINES_WITH_BUTTON) - 1]

i = 0
line_with_buttons_idx = 1
output_lines.append("<div hidden id=\"commentCodeID\">" + FILE_CODE_NAME +"</div>")
with open(INPUT_CODE) as f:
	for line in f:
		i += 1
		#print(line)
		# print(line)
		# print(line[0])
		# print(ord(line[0]))
		if line[-1] == "\n":
			line = line[:-1]
		code_line = line.replace('<','&lt;')
		# code_line = code_line.replace(' ',"&nbsp;")
		#code_line = code_line.replace('\t',"&emsp;")
		ans = ""
		ans += "<tr>\n"
		ans += "<td><pre><code class=\"language-c\">" + code_line + " </code></pre></td>\n"
		if i in LINES_WITH_BUTTON:
			print(i)
			lst = ""
			if i == LAST_COMMENT:
				lst = " (LAST)"
				print(i, lst)
			ans += "<td><button class=\"btnc\" type=\"button\" id=\"comment"+str(line_with_buttons_idx) +"\" onclick=\"openForm(this.id)\">Comment "+str(line_with_buttons_idx) + lst +"</button></td>\n"
			line_with_buttons_idx += 1
		ans += "</tr>\n"
		output_lines.append(ans)

with open('codes_output/'+FILE_CODE_NAME+".html", 'w') as f:
	with open('pre_html.txt') as f2:
		for line in f2:
			f.write(line)
	for line in output_lines:
		f.write(line)
	with open('post_html.txt') as f2:
		for line in f2:
			f.write(line)

