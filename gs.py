#! /usr/bin/env python
# coding=iso-8859-1

import sys
import getopt
import subprocess
import re
from datetime import date
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
		

class GitLogComando:

	def linhas(self, options=list()):
                comandoArray = ['git',
                                'log',
                                '--pretty=format:"%H|%an|%ae|%ai|%cn|%ce|%ci|%s"',
                                "--shortstat",
                                "--no-merges"]
                comandoArray.extend(options)
                print "Executando comando ... \n %s " % comandoArray
                comando = Comando(comandoArray)
                return comando.saida().splitlines();

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
	def create(autor, commit_stats):
		return CommitStats(
			arquivos  = int(re.search("\d*",statsValues[0].strip()).group(0)),
			insercoes = int(re.search("\d*",statsValues[1].strip()).group(0)),
			remocoes  = int(re.search("\d*",statsValues[2].strip()).group(0)))

	create = staticmethod(create)
	"""

	def total_modificado(self):
		return self.insercoes + self.remocoes

	
	def __str__(self):
		return "Commits: %4d, Modificações: %6d (+%d,-%d)" % (
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

class CommitFactory:

	def __init__(self, log_linhas):
		self.log_linhas = log_linhas

	def __clean_hash(self,rawHash):
		return rawHash[0:len(rawHash)]

	def __clean_msg(self,rawMsg):
		return rawMsg#rawMsg[0:len(rawMsg)-1] 
	
	def __parse_date(self, date):
		#ignoring timezone, python does not recognize %z option
		return datetime.strptime(date[0:19], "%Y-%m-%d %H:%M:%S")

	def __parse_qtd_arquivos(self, rawString):
		return int(re.search("\d*",rawString.strip()).group(0))

	def __parse_qtd_insercoes(self, rawString):
		return int(re.search("\d*",rawString.strip()).group(0))

	def __parse_qtd_remocoes(self, rawString):
		return int(re.search("\d*",rawString.strip()).group(0))

	def gera_commit(self, commit_string, commit_stats):
		commitValues = commit_string.split('|')
		statsValues  = commit_stats.split(',')

		return Commit(
			sha_hash    = self.__clean_hash(commitValues[0]),
			mensagem    = self.__clean_msg(commitValues[7]), 
			autor       = Pessoa(nome = commitValues[1], email = commitValues[2]), 
			data_autor  = self.__parse_date(commitValues[3]), 
			committer   = Pessoa(nome = commitValues[4], email = commitValues[5]), 
			data_commit = self.__parse_date(commitValues[6]),
			arquivos    = self.__parse_qtd_arquivos(statsValues[0]),
			insercoes   = self.__parse_qtd_insercoes(statsValues[1]),
			remocoes    = self.__parse_qtd_remocoes(statsValues[2]))


	def __has_more_elements(self, lista): 
		return bool(lista)

	def gera_commits(self):

		commits = list()

		while self.__has_more_elements(self.log_linhas):
			first_line = self.log_linhas.pop()
			#print "analyzing: " + first_line + ", " + str(len(first_line))

			while String(first_line).is_empty_string():
				#print "skiping empty line"
				if not self.__has_more_elements(self.log_linhas):
					return commits
				first_line = self.log_linhas.pop()

			second_line = self.log_linhas.pop();

			#print "Commit Stats: %s" % first_line
			#print "Commit Data:  %s" % second_line

			commit = self.gera_commit(commit_stats = first_line, commit_string = second_line)
			#print "Appending %s " % commit
			commits.append(commit)
		
		return commits


class String:
	
	def __init__(self, string):
		self.string = string

	def starts_with_icase(self, outro):
		return self.string.lower().startswith(outro.lower())

	def is_empty_string(self):
		return not self.string.strip()


class CommitFilter:

	def __init__(self, commits):
		self.commits = commits

	#filter todos os autores que comecam com nome_autor
	def filter_by_autor_nomes(self, nomes):
		temp_list = list()
		for commit in self.commits:
			for nome in nomes:
				nome = nome.strip()
				if String(commit.autor.nome).starts_with_icase(nome):
					temp_list.append(commit)
		return temp_list	


	def filter_by_date(self, date):
		return [commit for commit in self.commits if commit.data_autor >= date]

class CommitProjection:
	
	def __init__(self, commits):
		self.commits = commits

	def soma_todas_modificacoes(self):
		total_commits = len(self.commits)
		total_arquivos = 0
		total_insercoes = 0
		total_remocoes = 0
		last_commit = None
	
		for commit in self.commits:
			total_arquivos  += commit.arquivos
			total_insercoes += commit.insercoes
			total_remocoes  += commit.remocoes

		return CommitStats(total_arquivos, total_commits, total_insercoes, total_remocoes)


	def soma_commits_por_autor(self):
		commitsOrdenados = CommitClassification(self.commits).order_by_nome_autor()

		lista = list()	
		commits_do_autor = list()	
		previous = commitsOrdenados[0].autor

		for commit in commitsOrdenados:
			if commit.autor.nome != previous.nome:
				lista.append(self.gera_commit_stats_para_autor(previous, commits_do_autor))
				commits_do_autor = list()
			previous = commit.autor
			commits_do_autor.append(commit)

		lista.append(self.gera_commit_stats_para_autor(previous, commits_do_autor))
		return lista


	def gera_commit_stats_para_autor(self, autor, commits_do_autor):
		qtd_arquivos  = 0
		qtd_insercoes = 0
		qtd_remocoes  = 0

		for commit in commits_do_autor:
			qtd_arquivos  += commit.arquivos 
			qtd_insercoes += commit.insercoes
		qtd_remocoes  += commit.remocoes
		commit_statistic = CommitStats(qtd_arquivos, len(commits_do_autor), qtd_insercoes, qtd_remocoes)
		return (autor, commit_statistic)			


class CommitClassification:
	
	def __init__(self, commits):
		self.commits = commits


	def order_by_nome_autor(self):
		return sorted(self.commits, key=lambda commit: commit.autor.nome)

class CommitStatsFilter:
	
	def __init__(self, autor_stats):
		self.autor_stats = autor_stats

	def order_by_num_modificacoes(self):
		return sorted(self.autor_stats, key=lambda autor_stat: autor_stat[1].total_modificado(), reverse=True)


def main():
	"""
		Programa executa git log para extrair infos sobre commits. 

		Use --autor="Joao Silva"  ou -a Joao  para procurar por um autor 
		especifico.

		Autor: Nico Steppat
			   Bernardo Santos
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
	today = datetime.today()
	data = datetime(today.year, today.month, 1,0,0,0)
	for op, arg in opts:
		if op in ("-h", "--help"):
			print main.__doc__
			sys.exit(0)
		if op in ("-a", "--autor" ):
			#print "autor: %s " % arg
			nome_autor = arg	
		if op in ("-d", "--data" ):
			#print "data: %s " % arg
			data = date.strptime(arg, "%d/%m/%Y")
	
	#pega todos os commits do git log
	log_linhas = GitLogComando().linhas()

	#gera um objeto para cada commit
	commits = CommitFactory(log_linhas).gera_commits()
	
	print "\nGerando estatistica a partir %s " % datetime.strftime(data, "%d/%m/%Y")
	commits = CommitFilter(commits).filter_by_date(data)

	#check se precisa filtrar pelo nome do autor
	if nome_autor:
		nomes = nome_autor.split(',')
		commits = CommitFilter(commits).filter_by_autor_nome(nomes)
	
	#ordena commits pelo nome do autor
	commits = CommitClassification(commits).order_by_nome_autor()
	commits_stats = CommitProjection(commits).soma_commits_por_autor()
	commits_stats = CommitStatsFilter(commits_stats).order_by_num_modificacoes()
	#resultado = sorted(resultado , key=lambda commit: commit.commit_statistic.total_modificado())

	#saida
	print "\nTotal autores: %d " % len(commits_stats)
	print "Total commits: %d " % len(commits) 
	print ""
	for autor_stat in commits_stats:
		print "{0:30} {1:20}".format(autor_stat[0].nome[0:30], autor_stat[1])


if __name__ == '__main__':
	main()
	
