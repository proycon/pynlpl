###############################################################
#  PyNLPl - Moses formats
#       by Maarten van Gompel (proycon)
#       http://ilk.uvt.nl/~mvgompel
#       Induction for Linguistic Knowledge Research Group
#       Universiteit van Tilburg
#
#       Licensed under GPLv3
#
# This is a Python library classes and functions for 
# reading file-formats produced by Moses. Currently 
# contains only a class for reading a Moses PhraseTable.
# (migrated to pynlpl from pbmbmt)
#
###############################################################    

import sys
import bz2

class PhraseTable:
	def __init__(self,filename, quiet=False, delimiter="|||", score_column = 5, align2_column = 4):
		"""Load a phrase table from file into memory (memory intensive!)"""
		self.phrasetable = {}
		if filename.split(".")[-1] == "bz2":
			f = bz2.BZ2File(filename,'r')		
		else:
			f = open(filename,'r')
		linenum = 0
		while True:
			if not quiet:
				linenum += 1
				if (linenum % 100000) == 0:
					print >> sys.stderr, "Loading phrase-table: @%d" % linenum
			line = f.readline()
			if not line: 
				break

		 	#split into (trimmed) segments
			segments = [ segment.strip() for segment in line.split(delimiter) ]

			#Do we have a score associated?
			if score_column > 0 and len(segments) >= score_column:
				score = float(segments[score_column-1].strip().split(" ",1)[0]) #the 1rd number is p(source|target), 3rd number is p(target|source)
			else:
				score = 0

			if align2_column > 0:
				null_alignments = segments[align2_column].count("()")
			else:
				null_alignments = 0

			source = segments[0]
			target = segments[1]
			if not source in self.phrasetable:
				#new entry in phrase table
				self.phrasetable[source] = [ (target, score, null_alignments) ]
			else:
				#there are already one or more translations for this source phrase in the phrase table. Insert the new translation
				self.phrasetable[source].append( (target, score, null_alignments) )
						
		f.close()		

	def exists(self, phrase):
		"""Query if a certain phrase exist in the phrase table"""
		return (phrase in self.phrasetable)

	def __contains__(self, phrase):
		"""Query if a certain phrase exist in the phrase table"""
		return (phrase in self.phrasetable)

	def translations(self, phrase):
		"""Return a list of (translation, score, null_alignment) tuples"""
		return self.phrasetable[phrase]


	def __getitem__(self, phrase): #same as translations
		try:
			data = self.phrasetable[phrase]
		except:
			raise
		return data

