#! /usr/bin/env python

import subprocess
import re

class Comando:
	p = None
	output = None	

        def __init__(self, comandoArray):
		self.p = subprocess.Popen(comandoArray, stdout=subprocess.PIPE)
		self.__execute__()

	def __execute__(self):
		if self.output is None:
			self.output =self.p.communicate()[0]
		return self.output

	
	def saida(self):
		return self.output
		

class Pessoa:
	nome = None
	email = None

	def __init__(self, nome, email):
		self.nome = nome
		self.email = email

class CommitStats:
	qtdFiles=None
	insercoes=None
	remocoes=None

	def __init__(self, qtdFiles, insercoes, remocoes):
		self.qtdFiles=qtdFiles
		self.insercoes=insercoes
		self.remocoes=remocoes

	def create(statsString):
		statsValues=statsString.split(',')
		return CommitStats(
			qtdFiles=int(re.search("\d*",statsValues[0].strip()).group(0)),
			insercoes=int(re.search("\d*",statsValues[1].strip()).group(0)),
			remocoes=int(re.search("\d*",statsValues[2].strip()).group(0)))

	def total_changed():
		return self.insercoes + (self.remocoes * -1)

	create = staticmethod(create)


class Commit:
	autor = None
	autorData = None
	committer = None
	commitData=None
	shaHash=None
	message=None
	

	def __init__(self, shaHash, mensagem, autor, autorData, committer, commitData, commitStats):
		self.shaHash = shaHash
		self.mensagem = mensagem
		self.autor = autor
		self.autorData  = autorData
		self.committer = committer
		self.commitData = commitData
		self.commitStats = commitStats

	def __str__(self):
                return self.shaHash

	def create(commitString, statsString):
		commitValues=commitString.split('|')
		commitStats=CommitStats.create(statsString)
		return Commit(
			shaHash = commitValues[0][1:len(commitValues[0])],
			mensagem = commitValues[7][0:len(commitValues[7])-1], 
			autor = Pessoa(nome=commitValues[1], email=commitValues[2]), 
			autorData = commitValues[3], 
			committer = Pessoa(nome=commitValues[4], email=commitValues[5]), 
			commitData = commitValues[6],
			commitStats = commitStats)

	create = staticmethod(create)


comando = Comando(['git', 'log', '--pretty=format:"%H|%an|%ae|%ai|%cn|%ce|%ci|%s"', "--shortstat", "--no-merges"])
saida = comando.saida().splitlines()

commits = list()

while saida:
	#print "---------------------------"
	commitStats=saida.pop().strip()
	#print "analyzing: " + commitStats + ", " + str(len(commitStats))
	if not commitStats: 
		#print "skiped: " + commitStats
		commitStats=saida.pop()
	commitString=saida.pop();
	#print "CommitString: " + commitString
	#print "CommitStats:  " + commitStats
	#print commitStats.split(',')[1]
	commits.append(Commit.create(commitString, commitStats))

for commit in commits:
	print commit.mensagem 

	
