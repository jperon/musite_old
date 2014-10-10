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
    def supprimer(self,fichier):
        groupes = lister(fichier)
        try:
            del groupes[self.nom]
            with open(fichier,'w') as f:
                f.write(
                    '\n'.join(
                        [ '\t'.join((nom, ','.join([u for u in groupes[nom] if u]))) for nom in groupes.keys()]
                        ) + '\n'
                    )
        except KeyError: pass
    def ajouter(self,utilisateur,fichier):
        groupes = lister(fichier)
        if utilisateur not in groupes[self.nom]:
            groupes[self.nom].append(utilisateur)
            with open(fichier,'w') as f:
                f.write(
                    '\n'.join(
                        [ '\t'.join((nom, ','.join([u for u in groupes[nom] if u]))) for nom in groupes.keys()]
                        ) + '\n'
                    )
        else: raise DejaEnregistre(utilisateur,self.nom)
    def retirer(self,utilisateur,fichier):
        groupes = lister(fichier)
        groupes[self.nom] = [u for u in groupes[self.nom] if u != utilisateur]
        with open(fichier,'w') as f:
            f.write(
                '\n'.join(
                    [ '\t'.join((nom, ','.join([u for u in groupes[nom] if u]))) for nom in groupes.keys()]
                    ) + '\n'
                )
    

class GroupeExistant(Exception):
    pass
class DejaEnregistre(Exception):
    pass

if __name__ == '__main__':
    print(lister(s.argv[1]))
