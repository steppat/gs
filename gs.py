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
	#nome = None
	#email = None

	def __init__(self, nome, email):
		self.nome = nome
		self.email = email

	def __str__(self):
		return "%s, %s" % (self.nome, self.email)


class CommitStats:
	#arquivos=None #quantidade de arquivos
	#insercoes=None #quantidade de insercoes
	#remocoes=None #quantidade de remocoes

	def __init__(self, arquivos, insercoes, remocoes):
		self.arquivos=arquivos
		self.insercoes=insercoes
		self.remocoes=remocoes

	def create(statsString):
		statsValues = statsString.split(',')
		return CommitStats(
			arquivos  = int(re.search("\d*",statsValues[0].strip()).group(0)),
			insercoes = int(re.search("\d*",statsValues[1].strip()).group(0)),
			remocoes  = int(re.search("\d*",statsValues[2].strip()).group(0)))

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
	#sha_hash = None
	#mensagem = None
	#autor = None
	#data_autor = None
	#committer  = None
	#data_commit = None
	#commit_statistic = None
	

	def __init__(self, sha_hash, mensagem, autor, data_autor, committer, data_commit, commit_statistic):
		self.sha_hash = sha_hash
		self.mensagem = mensagem
		self.autor = autor
		self.data_autor  = data_autor
		self.committer = committer
		self.data_commit = data_commit
		self.commit_statistic = commit_statistic

	def __str__(self):
                return "%s, %s, %s, %s" % (self.sha_hash, self.mensagem, self.autor.nome, self.commit_statistic) 


class CommitsFactory:

	def __clean_hash(self,rawHash):
		return rawHash[1:len(rawHash)]

	def __clean_msg(self,rawMsg):
		return rawMsg[0:len(rawMsg)-1] 
	
	def __parse_date(self, date):
		#ignoring timezone, python does not recognize %z option
		return datetime.strptime(date[0:19], "%Y-%m-%d %H:%M:%S")

	def create_commit(self, commitString, statsString):
		commitValues = commitString.split('|')
		commit_statistic = CommitStats.create(statsString)

		return Commit(
			sha_hash    = self.__clean_hash(commitValues[0]),
			mensagem    = self.__clean_msg(commitValues[7]), 
			autor       = Pessoa(nome=commitValues[1], email=commitValues[2]), 
			data_autor  = self.__parse_date(commitValues[3]), 
			committer   = Pessoa(nome=commitValues[4], email=commitValues[5]), 
			data_commit = self.__parse_date(commitValues[6]),
			commit_statistic = commit_statistic)

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
			#print "CommitString: " + siecondLine
			commits.append(self.create_commit(commitString=secondLine, statsString=firstLine))
		
		return commits

#filter todos os autores que comecam com nome_autor
def filter_commits_by_autor_name(commits, nome_autor):
	return [commit for commit in commits if commit.autor.nome.lower().startswith(nome_autor.lower())]


def filter_commits_by_date(commits, date):
	return [commit for commit in commits if commit.data_autor >= date]


def soma_commits_stats(commits):
	total_arquivos = 0
	total_insercoes = 0
	total_remocoes = 0
	last_commit = None

	for commit in commits:
		total_arquivos  += commit.commit_statistic.arquivos
		total_insercoes += commit.commit_statistic.insercoes
		total_remocoes  += commit.commit_statistic.remocoes
		last_commit = commit 

	return Commit(
		sha_hash     = last_commit.sha_hash,
		mensagem    = last_commit.mensagem, 
		autor       = last_commit.autor, 
		data_autor  = last_commit.data_autor, 
		committer   = last_commit.committer, 
		data_commit = last_commit.data_commit,
		commit_statistic = CommitStats(total_arquivos, total_insercoes, total_remocoes))


def main():
	"""
		Programa executa git log para extrair infos sobre commits. 

		Use --autor="Joao Silva"  ou -a Joao  para procurar por um autor 
		especifico.

		Autor: Nico Steppat
	"""
	# parse command line options
	try:
		opts, args = getopt.getopt(sys.argv[1:], "had:", ["help", "autor=", "data="])
	except getopt.error, msg:
		print msg
		print "for help use --help"
		sys.exit(2)
	
	# process options
	nome_autor = None
	data = None
	for op, arg in opts:
		if op in ("-h", "--help"):
			print main.__doc__
			sys.exit(0)
		if op in ("-a", "--autor" ):
			#print "autor: %s " % arg
			nome_autor = arg	
		if op in ("-d", "--data" ):
			#print "data: %s " % arg
			data = datetime.strptime(arg, "%d/%m/%Y")

	commits = CommitsFactory().commits_from_git_log()
	commits = sorted(commits, key=lambda commit: commit.autor.nome)
	
	if nome_autor:
		print "Filtrando pelo autor %s" % nome_autor
		commits = filter_commits_by_autor_name(commits, nome_autor)

	if data:
		print "Filtrando pela data %s" % data
		commits = filter_commits_by_date(commits, data)

	soma = soma_commits_stats(commits)
	"""
	for commit in commits:
		print "Autor: %s, Msg: %s [Files: %d, Changes: %d (%d,%d)]" % (
			commit.autor.nome, 
			commit.mensagem,
			commit.commit_statistic.arquivos, 
			commit.commit_statistic.total_modificado(), 
			commit.commit_statistic.insercoes, 
			commit.commit_statistic.remocoes )
	"""
	print"Commits: %d, %s" % (len(commits), soma)

if __name__ == '__main__':
	main()
	
