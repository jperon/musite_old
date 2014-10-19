#!/usr/bin/env python3
import sys as s
import hashlib as h

def encoder(mdp):
    return h.sha1(mdp.encode('utf-8')).hexdigest()

def lister(fichier):
    with open(fichier,'r') as f:
        return {u[0]:u[1].replace('\n','')
            for u in [l.split('\t') for l in f.readlines()
                if '\t' in l]
            }

class Utilisateur:
    def __init__(self,nom,mdp=''):
        self.nom = nom
        self.mdp = encoder(mdp)
    def ajouter(self,fichier):
        if self.mdp == '': raise MotDePasseRequis
        if self.nom not in lister(fichier).keys():
            with open(fichier,'a') as f:
                f.write('{0}\t{1}\n'.format(self.nom,self.mdp))
        else: raise UtilisateurExistant(self.nom)
    def supprimer(self,fichier):
        utilisateurs = lister(fichier)
        try:
            del utilisateurs[self.nom]
            with open(fichier,'w') as f:
                for nom in utilisateurs.keys():
                    f.write('{0}\t{1}\n'.format(nom,utilisateurs[nom]))
        except KeyError:pass
    def modifier(self,fichier):
        if self.mdp == '': raise MotDePasseRequis
        utilisateurs = lister(fichier)
        utilisateurs[self.nom] = self.mdp
        with open(fichier,'w') as f:
            for nom in utilisateurs.keys():
                f.write('{0}\t{1}\n'.format(nom,utilisateurs[nom]))
    def __str__(self):
        return self.nom + '\t' + self.mdp
    def __repr__(self):
        return self.__str__()

class UtilisateurExistant(Exception):
    pass

class MotDePasseRequis(Exception):
    pass

if __name__ == '__main__':
    try:
        u = Utilisateur(s.argv[2],s.argv[3])
        {
            '-a':u.ajouter,
            '-s':u.supprimer,
            '-m':u.modifier}[s.argv[1]](s.argv[4])
    except IndexError: print(encoder(s.argv[1]))
