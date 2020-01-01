import os
import sys
import ntpath

INPUT_CODE = sys.argv[1] # Path to code file in codes/
FILE_NAME = INPUT_CODE[:INPUT_CODE.find(".")]	# File name (without the extension)

# Getting list of line numbers for which there needs to be a comment feedback button present.
LINES_WITH_BUTTON = []
with open(FILE_NAME+".lines") as f:
	for line in f:
		line_nos = line.split(" ")
		for ln in line_nos:
			LINES_WITH_BUTTON.append(int(ln))

# Getting the code file's name (without code/ path)
FILE_CODE_NAME = ntpath.basename(FILE_NAME)
output_lines = []
LAST_COMMENT = LINES_WITH_BUTTON[len(LINES_WITH_BUTTON) - 1]

# Building the HTML body content for the code
i = 0
line_with_buttons_idx = 1
# This hidden div contains code name to be used to code id field by the javascript.
output_lines.append("<div hidden id=\"commentCodeID\">" + FILE_CODE_NAME +"</div>")
with open(INPUT_CODE) as f:
	for line in f:
		i += 1
		if line[-1] == "\n":
			line = line[:-1]
		# We need to replace all '<' with '&lt;' in html.
		code_line = line.replace('<','&lt;')
		ans = ""
		ans += "<tr>\n"
		ans += "<td><pre><code class=\"language-c\">" + code_line + " </code></pre></td>\n"
		if i in LINES_WITH_BUTTON:
			print(i)
			# To append (LAST) in button text if it is the last button.
			lst = ""
			if i == LAST_COMMENT:
				lst = " (LAST)"
				print(i, lst)
			ans += "<td><button class=\"btnc\" type=\"button\" id=\"comment"+str(line_with_buttons_idx) +"\" onclick=\"openForm(this.id)\">Comment "+str(line_with_buttons_idx) + lst +"</button></td>\n"
			line_with_buttons_idx += 1
		ans += "</tr>\n"
		output_lines.append(ans)

with open('codes_output/'+FILE_CODE_NAME+".html", 'w') as f:
	# First append the pre html text (header, etc.)
	with open('pre_html.txt') as f2:
		for line in f2:
			f.write(line)
	# Append the HTML body that we built in this code.
	for line in output_lines:
		f.write(line)
	# Finally write the post part of html.
	with open('post_html.txt') as f2:
		for line in f2:
			f.write(line)
