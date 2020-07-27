from typing import Dict, Tuple, List, Union
from gopherpysat import Gophersat
import time
import random


__author__ = "Alicia BOULLEE, Simon DEVAUCHELLE,"
__copyright__ = "Copyright 2020, UTC"
__license__ = "LGPL-3.0"
__version__ = "0.30.0"
__maintainer__ = "Alicia BOULLEE? Simon DEVAUCHELLE"
__email__ = "alicia.boullee@etu.utc.fr"
__status__ = "dev"


REWARD = {"gold": 1000, "killed_wumpus": 500, "initial": 100}
COST = {
    "initial": 0,
    "step": 1,
    "arrow": 100,
    "percept": 1,
    "probe": 10,
    "failed_probe": 1000,
    "cautious_probe": 50,
    "death": 5000,
}
RATES = {"pit_rate": 0.25, "gold_rate": 0.025}

world1 = [
    ["", "", "P", ""],
    ["", "", "", ""],
    ["W", "G", "P", ""],
    ["", "", "", "P"],
]



gophersat_exec = "C:/Users/Simon/Desktop/projet_ia02/gophersat-1.1.6"
    

rand = random.Random()



def compute_stench(world: List[List[str]], n: int) -> List[List[str]]:
    for i in range(n):
        for j in range(n):
            if "W" in world[i][j]:
                if i + 1 < n and "S" not in world[i + 1][j]:
                    world[i + 1][j] += "S"
                if j + 1 < n and "S" not in world[i][j + 1]:
                    world[i][j + 1] += "S"
                if i - 1 >= 0 and "S" not in world[i - 1][j]:
                    world[i - 1][j] += "S"
                if j - 1 >= 0 and "S" not in world[i][j - 1]:
                    world[i][j - 1] += "S"
    return world

def compute_breeze(world: List[List[str]], n: int) -> List[List[str]]:
    for i in range(n):
        for j in range(n):
            if "P" in world[i][j]:
                if i + 1 < n and "B" not in world[i + 1][j]:
                    world[i + 1][j] += "B"
                if j + 1 < n and "B" not in world[i][j + 1]:
                    world[i][j + 1] += "B"
                if i - 1 >= 0 and "B" not in world[i - 1][j]:
                    world[i - 1][j] += "B"
                if j - 1 >= 0 and "B" not in world[i][j - 1]:
                    world[i][j - 1] += "B"

    return world


def compute_empty(world: List[List[str]], n: int) -> List[List[str]]:
    for i in range(n):
        for j in range(n):
            if world[i][j] == "":
                world[i][j] = "."
    return world


def random_world(n: int, pit_rate: float = 0.25, gold_rate: float = 0.025):
    # On commence par générer un monde vide
    world = [[""] * n for i in range(n)]

    # On génère aléatoirement la case sur laquelle va se trouver le Wumpus
    posw = (rand.randrange(n), rand.randrange(n))
    while posw == (0, 0):
        posw = (rand.randrange(n), rand.randrange(n))
    x, y = posw
    world[x][y] = "W"

    # On ajoute aléatoirement une pépite d'or (au minimum) sur la carte
    posg = (rand.randrange(n), rand.randrange(n))
    while posg == posw:
        posg = (rand.randrange(n), rand.randrange(n))
    x, y = posg
    world[x][y] = "G"

    for i in range(n):
        for j in range(n):
            if (i, j) != (0, 0) and "W" not in world[i][j]:
                r = rand.random()
                if r < RATES["pit_rate"] and "G" not in world[i][j]:

                    world[i][j] += "P"

                r = random.random()
                if r < RATES["gold_rate"] and "P" not in world[i][j]:
                    world[i][j] += "G"
                    
    world = compute_stench(world, n)
    world = compute_breeze(world, n)
    world = compute_empty(world, n)

    return world


def afficherMap(world: List[List[str]]) -> None:
    n = len(world)
    for i in range(n):
        print(f"{i}: ", end="")
        for j in range(n):
            print(world[i][j], end=" ")

        print()
    print


class WumpusWorld:
    def __init__(self, n: int = 4, rand: bool = False):
        self.__N = n
        self.__knowledge = [[False] * self.__N for i in range(self.__N)]

        if rand:
            self.__world = random_world(self.__N)
        else:
            self.__world = world1
            self.__world = compute_stench(self.__world, self.__N)
            self.__world = compute_breeze(self.__world, self.__N)
            self.__world = compute_empty(self.__world, self.__N)

        self.__position = (0, 0)
        self.__dead = False
        self.__gold_found = False

        self.__cost = COST["initial"]
        self.__reward = REWARD["initial"]

    def get_n(self):
        return self.__N

    def get_knowledge(self):
        res = [["?"] * self.__N for i in range(self.__N)]

        for i in range(self.__N):
            for j in range(self.__N):
                if self.__knowledge[i][j]:
                    res[i][j] = self.__world[i][j]

        return res

    def get_position(self) -> Tuple[int, int]:
        return self.__position

    def get_percepts(self) -> Tuple[str, str, str]:
        self.__cost += COST["percept"]

        i = self.__position[0]
        j = self.__position[1]
        self.__knowledge[i][j] = True

        return (f"[OK]", f'vous sentez {self.__world[i][j]}"', self.__world[i][j])

    def get_reward(self) -> int:
        return self.__reward

    def get_cost(self) -> int:
        return self.__cost

    def probe(self, i, j) -> Tuple[str, str, int]:
        self.__cost += COST["probe"]

        self.__position = (i, j)

        if i < 0 or j < 0 or i >= self.__N or j >= self.__N:
            return (
                "[err]",
                " impossible move, you lose {COST['probe']} coins",
                -COST["probe"],
            )

        content = self.__world[i][j]

        if "W" in content or "P" in content:
            self.__cost += COST["failed_probe"]
            return (
                "[KO]",
                f"The wizard catches a glimpse of the unthinkable and turns mad: you lose {COST['failed_probe']} coins",
                -COST["failed_probe"],
            )

        a, b, c = self.get_percepts()

        return (a, c, -COST["probe"])

    def cautious_probe(self, i, j) -> Tuple[str, str, int]:
        self.__cost += COST["cautious_probe"]

        self.__position = (i, j)

        if i < 0 or j < 0 or i >= self.__N or j >= self.__N:

            return (
                "[err]",
                " impossible move, you lose {COST['cautious_probe']} coins",
                -COST["cautious_probe"],
            )

        self.__position = (i, j)
        content = self.__world[i][j]

        a, b, c = self.get_percepts()

        return (a, c, -COST["cautious_probe"])

    def go_to(self, i, j) -> Tuple[str, str, Union[int, Tuple[int, int]]]:
        if i == 0 and j == 0 and self.__gold_found:
            return "[OK]", f"Vous avez trouvé {REWARD['gold']} pièces !", REWARD["gold"]

        if (
            abs(i - self.__position[0]) + abs(j - self.__position[1]) != 1
            or i < 0
            or j < 0
            or i >= self.__N
            or j >= self.__N
        ):
            return ("[err]", "Ce déplacement est impossible ! ", -COST["step"])

        self.__position = (i, j)
        content = self.__world[i][j]
        if "W" in content:
            self.__dead = True
            self.__cost += COST["death"]
            return (
                "[KO]",
                f"Malheureusement, vous avez rencontré le WUmpus, et celui-ci vous a vaincu ! Vous avez perdu ! Dommage !{COST['death']} coins",
                -COST["death"],
            )
        if "P" in content:
            self.__dead = True
            self.__cost += COST["death"]
            return (
                "[KO]",
                f"Malheur ! Vous êtes tombés dans un puit ! Vous avez perdu ! Dommage ! {COST['death']} coins",
                -COST["death"],
            )
        if "G" in content:
            self.__gold_found = True
            self.__reward += REWARD["gold"]
            return (
                "[OK]",
                f"Bravo à vous ! Vous avez trouvé l'or ! Vous avez gagné ! {REWARD['gold']} coins",
                REWARD["gold"],
            )

        return ("[OK]", f"Voici votre position :{self.__position}", self.__position)

    def __str__(self) -> str:
        s = ""
        for i in range(self.__N):
            s += f"{i}:"
            for j in range(self.__N):
                s += f" {self.__world[i][j]} "
            s += "\n"

        return s

class Case:
    def __init__(self, pos, g = 0, h = 0, f = 0):
        self.pos = pos
        self.g = g
        self.h = h
        self.f = f
        self.parent = None

    def calcul(self, pere, end):
        self.g = 10 + pere.g
        self.h = (abs(self.pos[0] - end.pos[0]) + abs(self.pos[1] - end.pos[1])) * 10
        self.f = self.h + self.g
        self.parent = pere

    def print(self):
        print("self.pos =", self.pos)
        print(" self.g =", self.g)
        print(" self.h =", self.h)
        print(" self.f =", self.f)
        if self.parent != None:
            print(" self.parent.pos =", self.parent.pos)

def clause_initialisation(ww):
    n = ww.get_n()
    voc = []
    for i in range(n):
        for j in range(n):
            voc.append("G(%s,%s)" % (i,j))
            voc.append("S(%s,%s)" % (i,j))
            voc.append("B(%s,%s)" % (i,j))
            voc.append("W(%s,%s)" % (i,j))
            voc.append("P(%s,%s)" % (i,j))

    gs = Gophersat(gophersat_exec, voc)

    gs.push_pretty_clause(["-P(0,0)"])
    gs.push_pretty_clause(["-W(0,0)"])

    for i in range(n):
        for j in range(n):
            gs.push_pretty_clause(["-W(%s,%s)" % (i,j), "-P(%s,%s)" % (i,j)])
            gs.push_pretty_clause(["-W(%s,%s)" % (i,j), "-G(%s,%s)" % (i,j)])
            gs.push_pretty_clause(["-P(%s,%s)" % (i,j), "-W(%s,%s)" % (i,j)])
            gs.push_pretty_clause(["-P(%s,%s)" % (i,j), "-G(%s,%s)" % (i,j)])
            strClausePitBreeze = ["-B(%s,%s)" % (i,j)]
            strClauseWumpusStench = ["-S(%s,%s)" % (i,j)]
            for e in successeur1([i, j], n):
                strClausePitBreeze.append("P(%s,%s)" % (e[0], e[1]))
                strClauseWumpusStench.append("W(%s,%s)" % (e[0], e[1]))
                gs.push_pretty_clause(["-P(%s,%s)" % (e[0], e[1]), "B(%s,%s)" % (i,j)])
                gs.push_pretty_clause(["-W(%s,%s)" % (e[0], e[1]), "S(%s,%s)" % (i,j)])
            gs.push_pretty_clause(strClausePitBreeze)
            gs.push_pretty_clause(strClauseWumpusStench)

    return gs


def ajouter_clause(gs, c, c_value):
    i = c[0]
    j = c[1]

    if c_value.find("B") >= 0:
        gs.push_pretty_clause(["B(%s,%s)" % (i,j)])
    else:
        gs.push_pretty_clause(["-B(%s,%s)" % (i,j)])
        
    if c_value.find("S") >= 0:
        gs.push_pretty_clause(["S(%s,%s)" % (i,j)])
    else:
        gs.push_pretty_clause(["-S(%s,%s)" % (i,j)])

    if c_value.find("P") >= 0:
        gs.push_pretty_clause(["P(%s,%s)" % (i,j)])
    else:
        gs.push_pretty_clause(["-P(%s,%s)" % (i,j)])

    if c_value.find("W") >= 0:
        gs.push_pretty_clause(["W(%s,%s)" % (i,j)])
    else:
        gs.push_pretty_clause(["-W(%s,%s)" % (i,j)])



def clause_deducted(c, gs, wwr, wfound):
    i = c[0]
    j = c[1]
    
    
 # On commence par vérifier qu'il n'y a pas de Wumpus
    if(not wfound):
        gs.push_pretty_clause(["-W(%s,%s)" % (i,j)])
        if not gs.solve():
            gs.pop_clause()
            a, b, c = wwr.cautious_probe(i, j)
            ajouter_clause(gs, [i,j], b)
            return True, b, True
        else:
            gs.pop_clause()
            
            
#On vérifie ensuite qu'il n'y a pas de puit
    gs.push_pretty_clause(["-P(%s,%s)" % (i,j)])
    if not gs.solve():
        gs.pop_clause()
        a, b, c = wwr.cautious_probe(i, j)
        ajouter_clause(gs, [i,j], b)
        return True, b, wfound
    else:
        gs.pop_clause()

#Enfin, on vérifie qu'il n'y a ni le Wumpus ni un puit
    gs.push_pretty_clause(["P(%s,%s)" % (i,j), "W(%s,%s)" % (i,j)])
    if not gs.solve():
        gs.pop_clause()
        a, b, c = wwr.probe(i, j)
        ajouter_clause(gs, [i, j], b)
        return True, b, wfound
    else:
        gs.pop_clause()

    return False, None, wfound



def parcours_map(succ, remove, insert, ww, gs):
    n = ww.get_n()
    l_safe = []
    l_nosafe = []
    l_known = []
    bloque = False
    WumpusFound = False
    last_l_nosafe = []


    a, b, c = ww.probe(0, 0)
    if (b.find("S") >= 0 or b.find("B") >= 0) :
        l_nosafe = insert([0,0], l_nosafe)
    else :
        l_safe = insert([0,0], l_safe)

    while (len(l_known) != n*n):
        while l_safe:
            c_safe, l_safe = remove(l_safe)
            if c_safe not in l_known:
                l_known.append(c_safe)
            for c2 in succ_inconnu(c_safe, n, l_known):
                a, b, c = ww.probe(c2[0],c2[1])
                l_known.append(c2)
                ajouter_clause(gs, c2, b)
                if (b.find("S") >= 0 or b.find("B") >= 0) :
                    l_nosafe = insert(c2, l_nosafe)
                else :
                    l_safe = insert(c2, l_safe)

        last_l_nosafe = l_nosafe
        next_l_nosafe=[]
        while l_nosafe:
            c_nosafe, l_nosafe = remove(l_nosafe)
            if c_nosafe not in l_known:
                l_known.append(c_nosafe)

            for c2 in succ_inconnu(c_nosafe, n, l_known):
                if bloque:
                    bloque = False
                    a, b, c = ww.cautious_probe(c2[0], c2[1])
                    l_known.append(c2)
                    ajouter_clause(gs, c2, b)
                    if (b.find("W") >= 0):
                        WumpusFound = True
                    if (b.find("S") >= 0 or b.find("B") >= 0) :
                        next_l_nosafe.append(c2)
                    else :
                        l_safe.append(c2)
                    

                else :
                    deduc, b, WumpusFound = clause_deducted(c2, gs, ww, WumpusFound)
                    if not deduc:
                        if c_nosafe not in next_l_nosafe:
                            next_l_nosafe.append(c_nosafe)
                    else:
                        if c2 not in l_known:
                            l_known.append(c2)
                        if (b.find("S") >= 0 or b.find("B") >=0) :
                            next_l_nosafe.append(c2)
                        else :
                            l_safe.append(c2)
        
        l_nosafe = next_l_nosafe
        if last_l_nosafe.sort() == next_l_nosafe.sort():
            bloque = True

def succ_inconnu(c, n, l_known):
    succ = successeur1(c, n)
    for x in l_known:
        if x in succ:
            succ.remove(x)

    return succ

def remove1(l):
    return l.pop(0), l

def insert1(s, l):
    l.append(s)
    return l

def successeur1(c, n):
    i = c[0]
    j = c[1]
    res= []
    if i + 1 < n:
        res.append([i + 1 , j])
    if i - 1 >= 0:
        res.append([i - 1 , j])
    if j + 1 < n:
        res.append([i , j + 1])
    if j - 1 >= 0:
        res.append([i , j - 1])
    return res


def tresor_liste(maze):
    i = 0
    j = 0
    gold = []
    for ligne in maze :
        for case in ligne :
            if case.find("G") >= 0:
                gold.append([i, j])
            j = j + 1
        i = i + 1
        j = 0
    return gold


def mur_liste(maze):
    l_wall = []
    i = 0
    j = 0
    for ligne in maze :
        for case in ligne :
            if case.find("P") >= 0 or case.find("W") >= 0:
                l_wall.append([i, j])
            j = j + 1
        i = i + 1
        j = 0
    return l_wall



def effectuer_analyse (pos, case, end):
    case_analyse = Case(pos)
    case_analyse.calcul(case, end)
    return case_analyse

def effectuer_analyse2 (pos, case, openList):
    for i in openList:
        if i.pos == pos:
            if (case.g + 10) < i.g:
                i.g = case.g + 10
                i.parent = case 
            return i

def sort(openList, case : Case):
    old_size = len(openList)
    indice = 0
    if case.pos in liste_position_c(openList):
        return openList
    for i in openList:
        if case.f < i.f and indice != 0:
            openList.insert(indice, case)
            return openList
        indice = indice + 1
    if old_size == len(openList):
        openList.append(case)
    return openList

def liste_position_c(l):
    l_pos = []
    for i in l:
        l_pos.append(i.pos)
    return l_pos

def succ(case : Case, end : Case, openList, pos_closelist, l_wall, n):
    i = case.pos[0]
    j = case.pos[1]
    l_analyse = []
    l_analyse_again = []
    if i + 1 < n:
        if ([i+1, j] not in l_wall and [i+1, j] not in pos_closelist):
            if [i+1, j] not in liste_position_c(openList):
                l_analyse.append([i+1 , j])
            else:
                l_analyse_again.append([i+1 , j])
    if i - 1 >= 0:
        if ([i-1, j] not in l_wall and [i-1, j] not in pos_closelist):
            if [i-1, j] not in liste_position_c(openList):
                l_analyse.append([i-1 , j])
            else:
                l_analyse_again.append([i-1 , j])
    if j + 1 < n:
        if ([i, j+1] not in l_wall and [i, j+1] not in pos_closelist):
            if [i, j+1] not in liste_position_c(openList):
                l_analyse.append([i , j+1])
            else:
                l_analyse_again.append([i , j+1])
    if j - 1 >= 0:
        if ([i, j-1] not in l_wall and [i, j-1] not in pos_closelist):
            if [i, j-1] not in liste_position_c(openList):
                l_analyse.append([i , j-1])
            else:
                l_analyse_again.append([i, j-1])

    for i in l_analyse:
        openList = sort(openList, effectuer_analyse(i, case, end))
    for i in l_analyse_again:
        openList = sort(openList, effectuer_analyse2(i, case, openList))
    return openList

def course_final(start : Case, end : Case, l_wall, n):
    #On commence par regarder ceux qui n'ont pas encore été analysés
    openList = [] 
    #On regarde ensuite ceux qui ont déjà été analysés
    closelist = [] 
    res = []
    current_case = start
    openList.append(start)

    while end.pos != current_case.pos:
        current_case = openList[0]
        openList = succ(current_case, end, openList, liste_position_c(closelist), l_wall, n)
        closelist.append(openList.pop(0))

        if len(openList) == 0 and end.pos != current_case.pos:
            print("Il n'y a pas de solution possible !")
            return res

    while current_case.parent != None :
        res.append(current_case.pos)
        current_case = current_case.parent
    res.append(start.pos)
    return res

def cheminFinal_emprunte(l_wall, l_gold, ww):
    case_start = Case([0, 0])
    l_final_path =[]
    final_path = []
    liste_case_final = []
    l_etat = []
    n = ww.get_n()
    nb_chemin = len(l_gold) 
    for i in l_gold:
        liste_case_final.append(i)

    while len(l_final_path) != nb_chemin:
        chemin = []
        while len(liste_case_final) != 0:
            case_gold = Case(liste_case_final.pop(0))
            path = course_final(case_start, case_gold, l_wall, n)
            if len(path) == 0 :
                return path
            
            if len(chemin) == 0 or len(chemin) > len(path):
                chemin = path
        case_start = Case(chemin[0])
        l_etat.append(chemin[0])
        for i in l_gold:
            if i not in l_etat:
                liste_case_final.append(i)
        l_final_path.append(chemin)

    indice = 0
    for i in l_final_path :
        i.reverse()
        print("Etape %s : %s" %(indice, i))
        indice = indice + 1
        i.reverse()

    indice = 0
    for chemin in l_final_path:
        chemin.reverse() 
        if indice > 0 :
            chemin.pop(0)
        for case in chemin:
            final_path.append(case)
        indice = indice + 1

    return final_path

def aller_tresor(ww, chemin_final):
    if len(chemin_final) != 0:
        chemin_final.pop(0)
        for case in chemin_final:
            ww.go_to(case[0], case[1])

if __name__ == "__main__":
    l_wall = []
    l_gold = []
    ww = WumpusWorld(10,True)
    gs = clause_initialisation(ww)
    start_time = time.time()
    parcours_map(successeur1, remove1, insert1, ww, gs)
    afficherMap(ww.get_knowledge())
    print(" ")
    print("Le coût est de ", ww.get_cost())
    print(" ")
    parcours_time = time.time() - start_time
    print(" 1 --- %s secondes ---" % parcours_time)
    print(" ")
    map = ww.get_knowledge()
    for i in map:
        print(i)
    l_wall = mur_liste(map)
    l_gold = tresor_liste(map)
    print("gold = ", l_gold)
    chemin = []
    chemin = cheminFinal_emprunte(l_wall, l_gold, ww)
    print("reward = ", ww.get_reward())
    aller_tresor(ww, chemin)
    print("reward = ", ww.get_reward())
    print("Bravo ! L'or a bien été récupéré")