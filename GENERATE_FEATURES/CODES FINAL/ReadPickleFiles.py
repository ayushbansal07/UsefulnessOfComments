#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  ReadPickleFiles.py
#  
#  Copyright 2018 Shakti <shakti@shakti-Inspiron-5559>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#  

import pickle
import os

def main(args):
	files = [f for f in os.listdir('.') if os.path.isfile(f)]
	for f in files:
		if f == 'data.p'  or f == 'PSemantic.p':
			continue
		if f.endswith(".p") :
			with open(f, 'rb') as fp:
				print("FileName = " + f)
				data = list(pickle.load(fp))
				print(len(data))
				for x in data :
					print()
					print()
					print()					
					print(x)
			print("--------------------------")
	return 0


if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
