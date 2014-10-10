#!/usr/bin/env python3
import sys as s


def lister(fichier):
    with open(fichier,'r') as f:
        return {g[0]:[u for u in g[1].replace('\n','').split(',')]
            for g in [l.split('\t') for l in f.readlines()
                if '\t' in l]
            }

class Groupe:
    def __init__(self,nom):
        self.nom = nom
    def creer(self,fichier):
        if self.nom not in lister(fichier).keys():
            with open(fichier,'a') as f:
                f.write('{0}\t\n'.format(self.nom))
        else: raise GroupeExistant(self.nom)
    def ajouter(self,utilisateur,fichier):
        groupes = lister(fichier)
        if utilisateur not in groupes[self.nom]:
            groupes[self.nom].append(utilisateur)
            

if __name__ == '__main__':
    print(lister(s.argv[1]))
