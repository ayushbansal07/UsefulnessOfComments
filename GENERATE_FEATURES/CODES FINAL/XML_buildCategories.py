import csv
import sys
import os
import re
import os
import pickle
import editdistance


# Text Categories code

CATEGORY_COUNT = 30
CAT_CONCEPTS_MATCH_SYMBOLS = 1
CAT_CONCEPTS_MATCH_TYPE = 2
CAT_CONCEPTS_NOT_MATCH_SYMBOLS = 3
CAT_CONCEPTS_PARTIALLY_MATCH_SYMBOLS = 4
CAT_CONCEPTS_MATCH_STRUCTURE = 5
CAT_NO_PROGRAM_DOMAIN_CONCEPTS = 6
CAT_NO_PROBLEM_DOMAIN_CONCEPTS = 7
CAT_LOW_PROGRAM_DOMAIN_CONCEPTS = 8
CAT_HIGH_PROGRAM_DOMAIN_CONCEPTS = 9
CAT_LOW_PROBLEM_DOMAIN_CONCEPTS = 10
CAT_HIGH_PROBLEM_DOMAIN_CONCEPTS = 11
CAT_CODE_COMMENT = 12
CAT_SHORT = 13
CAT_HIGH_SCOPE = 14
CAT_LOW_SCOPE = 15
CAT_COPYRIGHT_LICENSE = 16
CAT_DATE = 17
CAT_EMAIL = 18
CAT_CONTACT = 19
CAT_BUG_VERSION = 20
CAT_AUTHOR_NAME = 21
CAT_BUILD = 22
CAT_EXCEPTION = 23
CAT_PERFORMANCE = 24
CAT_DESIGN = 25
CAT_MEMORY = 26
CAT_SYSTEM_SPEC = 27
CAT_LIBRARY = 28
CAT_OUTPUT_RETURN = 29
CAT_JUNK = 30

def is_verb(tag):
	return tag in ['VB', 'VBZ', 'VBN', 'VBP', 'VBG', 'VBD']

def is_conditional(postags, dependencies):
	for postag in postags:
		if postag[1]=='IN':
			for dependency in dependencies:
				if dependency[1] == 'mark' and (dependency[0][1] == 'IN' or dependency[2][1] == 'IN'):
					return True
	return False

# use stanford parser to categories comments based on postags and dependencies
# list of categories:
# CONDITIONAL: contains 'IN' tag and has a 'mark' dependency involving the 'IN' tag
# NN_JJ_SYM_ROOT: there is a NN, JJ or SYM tag as ROOT
# VERB_ROOT:  there is a verb (VB, VBZ, VBN, VBP, VBG, VBD) tag as ROOT
# VERB_AUXILIARY: the ROOT is not verb, but there is an auxiliary verb
# 
def find_nlp_categories(comment):
	result = []

	postags = stanford_pos_tagger.tag(comment.split())
	raw_dependencies = [parse for parse in stanford_dep_parser.raw_parse(comment)]
	dependencies = [list(dep.triples()) for dep in raw_dependencies]

	#for now, assume a single dependency tree
	raw_dependencies = raw_dependencies[0]
	dependencies = dependencies[0]

	#check for each category

	if is_conditional(postags, dependencies):
		result.append('CONDITIONAL')

	if raw_dependencies.root['tag'] in ['NN', 'JJ', 'SYM']:
		result.append('NN_JJ_SYM_ROOT')

	if is_verb(raw_dependencies.root['tag']):
		result.append('VERB_ROOT')
	else:
		for postag in postags:
			if is_verb(postag[1]):
				result.append('VERB_AUXILIARY')
				break

	return result

def matches_with_keywords(text, keywords):
	text = text.lower()

	for keyword in keywords:
		if keyword in text:
			return 1

	return 0

def is_copyright_or_license_comment(comment):

	keywords = [
				"copyright", "copyleft", "copy-right", "license", "licence", "trademark", "open source", "open-source"
				]
	return matches_with_keywords(comment, keywords)

def is_bug_or_version_related_comment(comment):

	keywords = [
				" bug", "bug #", "bugid", "bug id", "bug number", "bug no", "bugno", "bugzilla",    # debug should not match
				" fix", "fix #", "fixid", "fix id", "fix number", "fix no", "fixno",   				# postfix, suffix etc should not match
				"patch", "patch #", "patchid", "patch id", "patch number", "patch no", "patchno",
				]

	return matches_with_keywords(comment, keywords) or \
		((re.search("bug [0-9]|fix [0-9]|version [0-9]", comment) is not None) and not is_copyright_or_license_comment(comment))



def is_build_related_comment(comment):

	keywords = [
				"cmake", "makefile", "build", "g++", "gcc", "dependencies", "apt-get",
				"git clone", "debug", "bin/"
				]

	return matches_with_keywords(comment, keywords)

def is_system_spec_related_comment(comment):

	keywords = [
				"ubuntu", "endian", "gpu", "hyperthreading", "32-bit", "64-bit", "128-bit", "configuration", "specification"
				"32bit", "64bit", "128bit", "configure"
				]

	return matches_with_keywords(comment, keywords) or (re.search("[0-9] [gG][bB]|[0-9] [mM][bB]|[0-9] [kK][bB]|Windows", comment) is not None)

def is_author_name_comment(comment):
	keywords = [
				"written by", "coded by", "developed by", "edited by", "modified by", "author", "contact",
				"fixed by"
				]
	return matches_with_keywords(comment, keywords)

def is_date_comment(comment):
	keywords = [
				"date of", "edited on", "written on", "created on", "modified on"
				]

	return matches_with_keywords(comment, keywords) or \
		(re.search("\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4}|\d{1,2}[\-\/][a-zA-Z]{3}[\-\/]\d{2,4}", comment) is not None)

def is_email_comment(comment):
	keywords = [
				"mail dot com", "mail dot in", "email"
				]

	return matches_with_keywords(comment, keywords) or \
		(re.search("([a-zA-Z0-9_\-\.]+)@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.)|(([a-zA-Z0-9\-]+\.)+))([a-zA-Z]{2,4}|[0-9]{1,3})(\]?)", comment) is not None)


def is_todo_comment(comment):

	keywords = ["todo", "to-do"]
	return matches_with_keywords(comment, keywords)

def is_junk_comment(comment):
	# there are no letters or numbers in the comment
	if re.search("[a-zA-Z0-9]", comment) is None:
		return 1
	return 0


def is_high_scope_comment(count):
	if count > 3:
		return 1
	return 0

def has_library_comment(comment):
	if comment.find(".h") != -1:
		return 1
	return 0

def isZero(x):
	if x == 0:
		return 1
	return 0

def isGreater(x, y):
	if x > y:
		return 1
	return 0

def readCSV(fname):
	f = open(fname, 'r')
	r = csv.reader(f)
	out = []
	for each in r:
		out.append(each)
	f.close()
	return out


def main():
	if len(sys.argv) != 3:
		print "Give 2 arguments, location of excel_file and location of features file"
		exit(-1)

	excel_file = sys.argv[1]
	features_file = sys.argv[2]
	
	base = readCSV(excel_file)
	features = readCSV(features_file)

	output = [['CAT_CONCEPTS_MATCH_SYMBOLS ', 'CAT_CONCEPTS_MATCH_TYPE ', 'CAT_CONCEPTS_NOT_MATCH_SYMBOLS ', 'CAT_CONCEPTS_PARTIALLY_MATCH_SYMBOLS ', 'CAT_CONCEPTS_MATCH_STRUCTURE ', 'CAT_NO_PROGRAM_DOMAIN_CONCEPTS ', 'CAT_NO_PROBLEM_DOMAIN_CONCEPTS ', 'CAT_LOW_PROGRAM_DOMAIN_CONCEPTS ', 'CAT_HIGH_PROGRAM_DOMAIN_CONCEPTS ', 'CAT_LOW_PROBLEM_DOMAIN_CONCEPTS ', 'CAT_HIGH_PROBLEM_DOMAIN_CONCEPTS ', 'CAT_CODE_COMMENT ', 'CAT_SHORT ', 'CAT_HIGH_SCOPE ', 'CAT_LOW_SCOPE ', 'CAT_COPYRIGHT_LICENSE ', 'CAT_DATE ', 'CAT_EMAIL ', 'CAT_CONTACT ', 'CAT_BUG_VERSION ', 'CAT_AUTHOR_NAME ', 'CAT_BUILD ', 'CAT_EXCEPTION ', 'CAT_PERFORMANCE ', 'CAT_DESIGN ', 'CAT_MEMORY ', 'CAT_SYSTEM_SPEC ', 'CAT_LIBRARY ', 'CAT_OUTPUT_RETURN ', 'CAT_JUNK ']]

	for i in range(1, len(base)):
		comment_text = base[i][2]

		categories = [0] * 30

		is_copyright_or_license = is_copyright_or_license_comment(comment_text)
		is_bug_or_version_related = is_bug_or_version_related_comment(comment_text)
		is_build_related = is_build_related_comment(comment_text)
		is_system_spec_related = is_system_spec_related_comment(comment_text)
		is_authorship_related = is_author_name_comment(comment_text)
		is_email = is_email_comment(comment_text)
		is_date = is_date_comment(comment_text)
		is_todo = is_todo_comment(comment_text)
		is_junk = is_junk_comment(comment_text)
		is_high_scope = is_high_scope_comment(features[i][6])
		has_library = has_library_comment(comment_text)

		categories[CAT_COPYRIGHT_LICENSE - 1] = is_copyright_or_license
		categories[CAT_DATE - 1] = is_date
		categories[CAT_EMAIL - 1] = is_email
		categories[CAT_BUG_VERSION - 1] = is_bug_or_version_related
		categories[CAT_AUTHOR_NAME - 1] = is_authorship_related
		categories[CAT_BUILD - 1] = is_build_related
		categories[CAT_SYSTEM_SPEC - 1] = is_system_spec_related
		categories[CAT_JUNK - 1] = is_junk
		categories[CAT_HIGH_SCOPE - 1] = is_high_scope
		categories[CAT_LOW_SCOPE - 1] = 1 - is_high_scope
		categories[CAT_LIBRARY - 1] = has_library

		no_program_domain_concepts = isZero(features[1])
		low_program_domain_concepts = 1 - isGreater(features[1], 3)
		high_program_domain_concepts = isGreater(features[1], 3)
		categories[CAT_LOW_PROGRAM_DOMAIN_CONCEPTS - 1] = low_program_domain_concepts
		categories[CAT_NO_PROGRAM_DOMAIN_CONCEPTS - 1] = no_program_domain_concepts
		categories[CAT_HIGH_PROBLEM_DOMAIN_CONCEPTS - 1] = high_program_domain_concepts

		output.append(categories)

	ofname = features_file.replace("feature", "categories")
	f = open(ofname, 'w')
	writer = csv.writer(f, delimiter=',', quoting=csv.QUOTE_NONNUMERIC)
	for each in output:
		writer.writerow(each)
	f.close()

main()
