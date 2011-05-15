#! /usr/bin/env python
# coding=iso-8859-1

import sys
import getopt
import subprocess
import re
from datetime import datetime



class Comando:
	p = None
	output = None	

        def __init__(self, comandoArray):
		self.p = subprocess.Popen(comandoArray, stdout=subprocess.PIPE)
		self.__execute()

	def __execute(self):
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

	def __str__(self):
		return "%s, %s" % (self.nome, self.email)


class CommitStats:
	arquivos=None #quantidade de arquivos
	insercoes=None #quantidade de insercoes
	remocoes=None #quantidade de remocoes

	def __init__(self, arquivos, insercoes, remocoes):
		self.arquivos=arquivos
		self.insercoes=insercoes
		self.remocoes=remocoes

	def create(statsString):
		statsValues=statsString.split(',')
		return CommitStats(
			arquivos=int(re.search("\d*",statsValues[0].strip()).group(0)),
			insercoes=int(re.search("\d*",statsValues[1].strip()).group(0)),
			remocoes=int(re.search("\d*",statsValues[2].strip()).group(0)))

	def total_modificado(self):
		return self.insercoes + self.remocoes

	
	def __str__(self):
		return "Arquivos totais: %d, Modificoes totais %d (+%d,-%d)" % (
			self.arquivos, 
			self.total_modificado(), 
			self.insercoes,
			self.remocoes)

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

class CommitsFactory:

	def __clean_hash(self,rawHash):
		return rawHash[1:len(rawHash[0])]

	def __clean_msg(self,rawMsg):
		return rawMsg[0:len(rawMsg)-1] 
	
	def __parse_date(self, date):
		#ignoring timezone, python does not recognize %z option
		return datetime.strptime(date[0:19], "%Y-%m-%d %H:%M:%S")


	def create_commit(self, commitString, statsString):
		commitValues=commitString.split('|')
		commitStats=CommitStats.create(statsString)

		return Commit(
			shaHash     = self.__clean_hash(commitValues[0]),
			mensagem    = self.__clean_msg(commitValues[7]), 
			autor       = Pessoa(nome=commitValues[1], email=commitValues[2]), 
			autorData   = self.__parse_date(commitValues[3]), 
			committer   = Pessoa(nome=commitValues[4], email=commitValues[5]), 
			commitData  = self.__parse_date(commitValues[6]),
			commitStats = commitStats)


	def git_log(self, options=list()):
		comandoArray = ['git', 
				'log', 
				'--pretty=format:"%H|%an|%ae|%ai|%cn|%ce|%ci|%s"', 
				"--shortstat", 
				"--no-merges"]
		comandoArray.extend(options)
		print "Executing: %s " % comandoArray
		comando = Comando(comandoArray)
		return comando.saida().splitlines();

	def commits_from_git_log(self):
		logLines = self.git_log()

		commits = list()

		while logLines:
			firstLine = logLines.pop().strip()
			#print "analyzing: " + firstLine + ", " + str(len(firstLine))
			if not firstLine: 
				#print "skiped: " + firstLine
				firstLine = logLines.pop()
			secondLine = logLines.pop();
			#print "CommitStats:  " + firstLine
			#print "CommitString: " + secondLine
			commits.append(self.create_commit(commitString=secondLine, statsString=firstLine))
		
		return commits

#fitler todos os autores que comecam com o nomeAutor
def filter_commits_by_autor_name(commits, nomeAutor):
	return [commit for commit in commits if commit.autor.nome.lower().startswith(nomeAutor.lower())]

def soma_commits_stats(commits):
	total_arquivos = 0
	total_insercoes = 0
	total_remocoes = 0
	for commit in commits:
			total_arquivos  += commit.commitStats.arquivos
			total_insercoes += commit.commitStats.insercoes
			total_remocoes  += commit.commitStats.remocoes
	return CommitStats(total_arquivos, total_insercoes, total_remocoes);

def main():
	# parse command line options
	try:
		opts, args = getopt.getopt(sys.argv[1:], "h", ["help"])
	except getopt.error, msg:
		print msg
		print "for help use --help"
		sys.exit(2)
	# process options
	for o, a in opts:
		if o in ("-h", "--help"):
			print __doc__
			sys.exit(0)
    	# process arguments
    	print args # process() is defined elsewhere

	nome='sérgio'
	commits = CommitsFactory().commits_from_git_log()
	commits = filter_commits_by_autor_name(commits, nome)
	soma = soma_commits_stats(commits)
	"""
	for commit in commits:
		print "Msg: %s, Autor: %s [Files: %d, Changes: %d (%d,%d)]" % (
			commit.mensagem, 
			commit.autor.nome,
			commit.commitStats.arquivos, 
			commit.commitStats.total_modificado(), 
			commit.commitStats.insercoes, 
			commit.commitStats.remocoes )
	"""
	print"Autor: %s, Commits: %d, %s" % (nome, len(commits), soma)

if __name__ == '__main__':
	main()
	
