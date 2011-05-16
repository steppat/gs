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

	def __init__(self, arquivos, commits, insercoes, remocoes):
		self.commits  = commits
		self.arquivos  = arquivos
		self.insercoes = insercoes
		self.remocoes  = remocoes

	"""
	def create(autor, statsString):
		return CommitStats(
			arquivos  = int(re.search("\d*",statsValues[0].strip()).group(0)),
			insercoes = int(re.search("\d*",statsValues[1].strip()).group(0)),
			remocoes  = int(re.search("\d*",statsValues[2].strip()).group(0)))

	create = staticmethod(create)
	"""

	def total_modificado(self):
		return self.insercoes + self.remocoes

	
	def __str__(self):
		return "Arquivos totais: %d, commits: %d modificoes: %d (+%d,-%d)" % (
			self.arquivos, 
			self.commits,
			self.total_modificado(), 
			self.insercoes,
			self.remocoes)



class Commit:

	def __init__(self, sha_hash, mensagem, autor, data_autor, committer, data_commit, arquivos, insercoes, remocoes):
		self.sha_hash = sha_hash
		self.mensagem = mensagem
		self.autor = autor
		self.data_autor  = data_autor
		self.committer = committer
		self.data_commit = data_commit
		self.arquivos  = arquivos
		self.insercoes = insercoes
		self.remocoes  = remocoes

	def total_modificado(self):
		return self.insercoes + self.remocoes

	def __str__(self):
                return " %s, %s" % (self.mensagem, self.autor) 

class CommitsFactory:

	def __clean_hash(self,rawHash):
		return rawHash[1:len(rawHash)]

	def __clean_msg(self,rawMsg):
		return rawMsg[0:len(rawMsg)-1] 
	
	def __parse_date(self, date):
		#ignoring timezone, python does not recognize %z option
		return datetime.strptime(date[0:19], "%Y-%m-%d %H:%M:%S")

	def __parse_qtd_arquivos(self, rawString):
		return int(re.search("\d*",rawString.strip()).group(0))

	def __parse_qtd_insercoes(self, rawString):
		return int(re.search("\d*",rawString.strip()).group(0))

	def __parse_qtd_remocoes(self, rawString):
		return int(re.search("\d*",rawString.strip()).group(0))

	def create_commit(self, commitString, statsString):
		commitValues = commitString.split('|')
		statsValues  = statsString.split(',')

		return Commit(
			sha_hash    = self.__clean_hash(commitValues[0]),
			mensagem    = self.__clean_msg(commitValues[7]), 
			autor       = Pessoa(nome = commitValues[1], email = commitValues[2]), 
			data_autor  = self.__parse_date(commitValues[3]), 
			committer   = Pessoa(nome=commitValues[4], email=commitValues[5]), 
			data_commit = self.__parse_date(commitValues[6]),
			arquivos    = self.__parse_qtd_arquivos(statsValues[0]),
			insercoes   = self.__parse_qtd_insercoes(statsValues[1]),
			remocoes    = self.__parse_qtd_remocoes(statsValues[2]))

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
def filter_commits_by_autor_name(commits, nomes):
	temp_list = list()
	for commit in commits:
		for nome in nomes:
			nome = nome.strip()
			if commit.autor.nome.lower().startswith(nome.lower()):
				temp_list.append(commit)
	return temp_list	


def filter_commits_by_date(commits, date):
	return [commit for commit in commits if commit.data_autor >= date]


def soma_todos_commits_stats(commits):
	total_commits = len(commits)
	total_arquivos = 0
	total_insercoes = 0
	total_remocoes = 0
	last_commit = None
	
	for commit in commits:
		total_arquivos  += commit.arquivos
		total_insercoes += commit.insercoes
		total_remocoes  += commit.remocoes

	return CommitStats(total_arquivos, total_commits, total_insercoes, total_remocoes)


def soma_commits_de_cada_autor(commits):
	commits = sorted(commits, key=lambda commit: commit.autor.nome)

	stats = list()	
	commits_do_autor = list()	
	autor = commits[0].autor

	for commit in commits:
		if commit.autor.nome == autor.nome:
			commits_do_autor.append(commit)
		else:
			stats.append(gera_commit_stats_para_autor(autor, commits_do_autor))
		autor = commit.autor

	stats.append(gera_commit_stats_para_autor(autor, commits_do_autor))
	return stats

def gera_commit_stats_para_autor(autor,commits):
	qtd_arquivos  = 0
	qtd_insercoes = 0
	qtd_remocoes  = 0

	for commit in commits:
		qtd_arquivos  += commit.arquivos 
		qtd_insercoes += commit.insercoes
		qtd_remocoes  += commit.remocoes
	commit_statistic = CommitStats(qtd_arquivos, len(commits), qtd_insercoes, qtd_remocoes)
	return (autor, commit_statistic)			

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

	#pega todos os commits do git log
	commits = CommitsFactory().commits_from_git_log()
	
	#check se precisa filtrar pela data
	if data:
		print "Filtrando pela data %s" % data
		commits = filter_commits_by_date(commits, data)

	#check se precisa filtrar pelo nome do autor
	if nome_autor:
		nomes = nome_autor.split(',')
		commits = filter_commits_by_autor_name(commits, nomes)
	
	#ordena commits pelo nome do autor
	commits = sorted(commits, key=lambda commit: commit.autor.nome)
	commits_stats  = soma_commits_de_cada_autor(commits)
	#resultado = sorted(resultado , key=lambda commit: commit.commit_statistic.total_modificado())

	print "Total commits %d " % len(commits) 
	#for c in resultado:
	#	print"Msg: %s, %s, Modificacoes: %d (%d, %d)" % (c.mensagem, c.autor.nome, c.total_modificado(), c.insercoes, c.remocoes)

	print "Total autores %d " % len(commits_stats)
	for autor_stat in commits_stats:
		print"Msg: %s, %s" % (autor_stat[0].nome, autor_stat[1])


if __name__ == '__main__':
	main()
	
