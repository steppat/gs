from gs import Pessoa
from gs import CommitStats
from gs import CommitStatsClassification
from gs import CommitFactory
from gs import Commit
from datetime import datetime

import unittest

def create_commit(nome_autor="nico"):
	pessoa = Pessoa(nome_autor, "nico@email.com")
	date = datetime.strptime("01/05/2011 15:30:10", "%d/%m/%Y %H:%M:%S")
	return Commit(
			sha_hash = "3a4f5b", 
			mensagem = "initial commit", 
			autor = pessoa, 
			data_autor  = date, 
			committer   = pessoa,
			data_commit = date, 
			arquivos  = 1, 
			insercoes = 2, 
			remocoes  = 3)
def create_commit_stats(total_arquivos, total_commits, total_insercoes, total_remocoes):
	autor = Pessoa("nico", "nico@email.com")
	return (autor, CommitStats(total_arquivos, total_commits, total_insercoes, total_remocoes))

class CommitStatsTest(unittest.TestCase):

	def test_commit_stats_somam_modificacoes(self):
		cs = CommitStats(1,1,2,3)
		self.assertEqual(5,cs.total_modificado())


class CommitTest(unittest.TestCase):
	
	def test_commit_soma_modificacoes(self):
		c = create_commit();
		self.assertEqual(5,c.total_modificado())



class CommitFactoryTest(unittest.TestCase):

	def __commit_string(self):
		s = str("e8308a05426ba7ab71cc91f70d8b943ce72b84a4|Nico Steppat|" +
			"nico.steppat@caelum.com.br|2011-05-14 15:30:56 -0300|" + 
			"Nico Steppat|nico.steppat@caelum.com.br|2011-05-14 15:30:56 -300|Initial commit")
		return s

	def __commit_stats(self):
		return "1 files changed, 112 insertions(+), 34 deletions(-)"

	def test_gera_um_commit_from_log(self):
		log = list()
		log.append("")
		log.append(self.__commit_string())
		log.append(self.__commit_stats())
		log.append("")
		fac = CommitFactory(log)
		commits = fac.gera_commits()
		self.assertEqual(1,len(commits))

	def test_gera_two_commits_from_log(self):
		log = list()
		log.append(self.__commit_string())
		log.append(self.__commit_stats())
		log.append("")
		log.append("")
		log.append("")
		log.append(self.__commit_string())
		log.append(self.__commit_stats())
		log.append("")
		fac = CommitFactory(log)
		commits = fac.gera_commits()
		self.assertEqual(2,len(commits))
	

	def test_gera_nenhum_commit_from_empty_list(self):
		log = list()
		fac = CommitFactory(log)
		commits = fac.gera_commits()
		self.assertEqual(0,len(commits))
	

	def test_gera_nenhum_commit_from_empty_log(self):
		log = list()
		log.append("")
		log.append("")
		log.append("")
		fac = CommitFactory(log)
		commits = fac.gera_commits()
		self.assertEqual(0,len(commits))

		#s = str("e8308a05426ba7ab71cc91f70d8b943ce72b84a4|Nico Steppat|" +
		#	"nico.steppat@caelum.com.br|2011-05-14 15:30:56 -0300|" + 
		#	"Nico Steppat|nico.steppat@caelum.com.br|2011-05-14 15:30:56 -300|Initial commit")

	def test_gera_commit_from_string(self):
		fac = CommitFactory(list())
		data = datetime.strptime("2011-05-14 15:30:56","%Y-%m-%d %H:%M:%S" )
		commit = fac.gera_commit(commit_string = self.__commit_string(), commit_stats = self.__commit_stats())
		self.assertEqual("Nico Steppat", commit.autor.nome)
		self.assertEqual("nico.steppat@caelum.com.br", commit.autor.email)
		self.assertEqual(data, commit.data_autor)
		self.assertEqual("Nico Steppat", commit.committer.nome)
		self.assertEqual("nico.steppat@caelum.com.br", commit.committer.email)
		self.assertEqual(data, commit.data_commit)
		self.assertEqual("e8308a05426ba7ab71cc91f70d8b943ce72b84a4", commit.sha_hash)
		self.assertEqual("Initial commit", commit.mensagem)

class CommitStatsClassificationTest(unittest.TestCase):
	def test_classific_por_modificacoes(self):
		stats = []
		stats.append(create_commit_stats(1,1,1,1))
		stats.append(create_commit_stats(2,2,2,2))
		stats.append(create_commit_stats(3,3,3,3))
		stats.append(create_commit_stats(4,4,4,4))
		ordenado = CommitStatsClassification(stats).order_by_modificacoes()
		self.assertEqual(2, (ordenado[-1][1].insercoes + ordenado[-1][1].remocoes))
		self.assertEqual(8, (ordenado[0][1].insercoes + ordenado[0][1].remocoes))
	
	def test_clasiffic_por_autor(self):
		stats = []
		stat1 = create_commit_stats(1,1,1,1)
		stat1[0].nome = "Bernardo"
		stats.append(stat1)

		stat2 = create_commit_stats(1,1,1,1)
		stat2[0].nome = "Nico"
		stats.append(stat2)

		ordenado = CommitStatsClassification(stats).order_by_autor()
		self.assertEqual("Bernardo", ordenado[0][0].nome)
		self.assertEqual("Nico", ordenado[-1][0].nome)
	
	def test_classifc_por_commit(self):
		stats = []
		stats.append(create_commit_stats(2,2,2,2))
		stats.append(create_commit_stats(4,4,4,4))
		ordenado = CommitStatsClassification(stats).order_by_commit()
		self.assertEqual(4, ordenado[0][1].commits)
		self.assertEqual(2, ordenado[-1][1].commits)

if __name__ == "__main__":
    unittest.main() 
