import os,hashlib
import random as r
import cherrypy as cp
import utilisateurs as u, groupes as g, jrnl as l

PWD = os.path.abspath(os.getcwd())

ticket = ''

def crypter(mdp):
    '''Encodage des mots de passe.'''
    mdp = mdp.encode('utf-8')
    return hashlib.sha1(mdp).hexdigest()

def utilisateurs():
    '''Liste des utilisateurs'''
    return u.lister(os.path.join(PWD,'etc','utilisateurs'))

def groupes():
    '''Liste des groupes.'''
    return g.lister(os.path.join(PWD,'etc','groupes'))

def authentifier(royaume,nom,mdp):
    try:
        if utilisateurs()[nom] == crypter(mdp):
            return valider(nom)
        else: return False
    except KeyError:
        return False

def valider(nom):
    if 'utilisateur' in passeport:
        return (nom == passeport['utilisateur'])
    elif 'utilisateurs' in passeport:
        return (nom in passeport['utilisateurs'].keys())
    elif 'groupe' in passeport:
        return (nom in groupes()[passeport['groupe']])

def reserver(**critere):
    def decorateur(fonction):
        def afficher(arg):
            global passeport
            passeport = critere
            if cp.lib.auth_basic.basic_auth('Droits insuffisants',authentifier) == None:
                global ticket
                cp.session['ticket'] = ticket = r.random()
                cp.session['nom'] = cp.request.login
                return fonction(arg)
            else:return '''Accès interdit'''
        return afficher
    return decorateur

def seulement(**critere):
    def decorateur(fonction):
        def afficher(*args):
            global passeport
            passeport = critere
            try:
                if cp.session['ticket'] == ticket and valider(cp.session['nom']):
                        return fonction(*args)
                else: return ''
            except KeyError: return ''
        return afficher
    return decorateur

def exclure(**critere):
    def decorateur(fonction):
        def afficher(*args):
            global passeport
            passeport = critere
            try:
                if cp.session['ticket'] == ticket and valider(cp.session['nom']):
                        return ''
                else: return fonction(*args)
            except KeyError: return fonction(*args)
        return afficher
    return decorateur
