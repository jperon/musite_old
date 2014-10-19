import os,hashlib
import random as r
import cherrypy as cp
import utilisateurs as u, jrnl as l

PWD = os.path.abspath(os.getcwd())

def crypter(mdp):
    '''Encodage des mots de passe.'''
    mdp = mdp.encode('utf-8')
    return hashlib.sha1(mdp).hexdigest()

def utilisateurs():
    '''Liste des utilisateurs'''
    return u.lister(os.path.join(PWD,'etc','utilisateurs'))

def groupes():
    '''Liste des groupes.'''
    return u.listergroupes(os.path.join(PWD,'etc','groupes'))

def authentifier(royaume,nom,mdp):
    '''Vérification des identifiants.'''
    try:
        if utilisateurs()[nom] == crypter(mdp):
            return valider(nom)
        else: return False
    except KeyError:
        return False

def valider(nom):
    '''Validation de la correspondance à un nom ou de l'appartenance
    à un groupe.'''
    if 'utilisateur' in passeport:
        return (nom == passeport['utilisateur'])
    elif 'utilisateurs' in passeport:
        return (nom in passeport['utilisateurs'].keys())
    elif 'groupe' in passeport:
        return (nom in groupes()[passeport['groupe']])

def reserver(**critere):
    '''Décorateur s'assurant de l'authentification avant d'assurer
    l'accès à une page.'''
    def decorateur(fonction):
        def afficher(*arg,**parms):
            global passeport
            passeport = critere
            if cp.lib.auth_basic.basic_auth('Droits insuffisants',authentifier) == None:
                cp.session['identifié'] = True
                cp.session['nom'] = cp.request.login
                return fonction(*arg,**parms)
            else:return '''Accès interdit'''
        return afficher
    return decorateur

def seulement(**critere):
    '''Décorateur permettant de réserver l'affichage de certains
    éléments aux utilisateurs identifiés, selon certains critères.
    N.B: cette fonction ne s'assure pas que l'identification soit
    authentique : pour cela, utilisez reserver.'''
    def decorateur(fonction):
        def afficher(*args):
            global passeport
            passeport = critere
            try:
                if cp.session['identifié'] == True and valider(cp.session['nom']):
                        return fonction(*args)
                else: return ''
            except KeyError: return ''
        return afficher
    return decorateur

def exclure(**critere):
    '''Décorateur permettant d'empêcher l'affichage de certains
    éléments pour les utilisateurs identifiés, selon certains critères.
    N.B: cette fonction ne s'assure pas que l'identification soit
    authentique : pour cela, utilisez reserver.'''
    def decorateur(fonction):
        def afficher(*args):
            global passeport
            passeport = critere
            try:
                if cp.session['identifié'] == True and valider(cp.session['nom']):
                        return ''
                else: return fonction(*args)
            except KeyError: return fonction(*args)
        return afficher
    return decorateur
