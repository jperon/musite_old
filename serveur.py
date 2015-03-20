#!/usr/bin/env python3
'''
Partie principale : lance le serveur web et appelle les modules
'''
import os
import sys
from string import Template
sys.path.insert(0, './etc')
sys.path.insert(0, './lib')
sys.path.insert(0, './lib/plugins')
import html
import cherrypy as cp
import config as c
import auth as a
import outils as s
import utilisateurs as u

PLUGINS = {}
for m in c.PLUGINS:
    PLUGINS[m] = __import__(m)


def presenter(retourner, plugin):
    '''Chargement des plugins.'''
    @cp.expose
    def retour(*arguments, **parametres):
        '''Décorateur'''
        cp.session['plugin'] = plugin
        return retourner(*arguments, **parametres)
    return retour


class Site:
    '''Cœur du site : chaque méthode décorée par cp.expose
    est accessible depuis un navigateur ; si elle est décorée par
    s.page, c'est une page.'''
    @cp.expose
    @s.page
    def index(self):
        '''Page d'accueil.'''
        with open('lib/index.html', 'r') as fichier:
            return fichier.read(-1)

    @cp.expose
    @s.page
    @a.reserver(utilisateurs=a.utilisateurs())
    def authentification(self):
        '''Page sans grand intérêt, si ce n'est de forcer
        l'authentification des utilisateurs.'''
        return 'Bonjour, {0} !'.format(cp.request.login)

    @cp.expose
    def css(self):
        '''Feuille de styles.'''
        with open(os.path.join('modeles', 'style.css')) as fichier:
            css = Template(fichier.read(-1))
        try:
            plugin = PLUGINS[cp.session['plugin']].css()
        except (AttributeError, KeyError):
            plugin = ''
        return css.substitute(plugin=plugin)


class Admin():
    '''Pages réservées à l'administration.'''
    @cp.expose
    @s.page
    @a.reserver(groupe='admin')
    def index(self):
        '''Page d'accueil des administrateurs.'''
        return 'Bonjour, {0} !'.format(cp.request.login)

    @cp.expose
    @s.page
    @a.reserver(groupe='admin')
    def utilisateurs(self, **parametres):
        '''Page de gestion des utilisateurs.'''
        with \
                open(os.path.join('lib', 'utilisateurs.html')) as fichier,\
                open(os.path.join('etc', 'groupes'), 'r') as grfichier:
            utilisateurs = Template(fichier.read(-1)).substitute(
                liste='\n'.join([
                    (
                        '<tr><td>'
                        + '{0}'
                        + '&nbsp&nbsp&nbsp'
                        + '</td><td><small>'
                        + '<a href=/admin/supprimerutilisateur/?nom={0}>'
                        + 'supprimer'
                        + '</a>'
                        + '</small></td></tr>'
                    ).format(u) for u in sorted(a.utilisateurs().keys())
                    ]),
                texte=parametres['texte']
                if 'texte' in parametres else '',
                groupes=grfichier.read(-1)
                )
        return utilisateurs

    @cp.expose
    @a.reserver(groupe='admin')
    def creerutilisateur(self, nom, mdp, mdp_v):
        '''Création d'un nouvel utilisateur.'''
        if mdp == mdp_v:
            utilisateur = u.Utilisateur(html.escape(nom), html.escape(mdp))
            try:
                utilisateur.ajouter(os.path.join('etc', 'utilisateurs'))
            except u.UtilisateurExistant:
                utilisateur.modifier(os.path.join('etc', 'utilisateurs'))
            raise cp.HTTPRedirect('/admin/utilisateurs/')
        else:
            return self.utilisateurs(
                texte='Les mots de passe ne correspondent pas.'
                )

    @cp.expose
    @a.reserver(groupe='admin')
    def enregistrergroupes(self, texte):
        '''Enregistrement des nouveaux paramètres de groupes'''
        with open(os.path.join('etc', 'groupes'), 'w') as fichier:
            fichier.write(html.escape(texte))
        raise cp.HTTPRedirect('/admin/utilisateurs/')

    @cp.expose
    @a.reserver(groupe='admin')
    def supprimerutilisateur(self, nom):
        '''Suppression d'un utilisateur.'''
        u.Utilisateur(html.escape(nom)).supprimer(
            os.path.join('etc', 'utilisateurs')
            )
        raise cp.HTTPRedirect('/admin/utilisateurs/')


if __name__ == '__main__':
    SITE = Site()
    for m in c.PLUGINS:
        setattr(SITE, m, presenter(PLUGINS[m].retourner, m))
    setattr(SITE, 'admin', Admin())

    @s.page
    def erreur_401(**args):
        '''Si un utilisateur cherche à atteindre une page réservée.'''
        return 'Accès réservé'
    cp.config.update({'error_page.401': erreur_401})
    cp.config.update(c.SERVER_CONFIG)
    cp.quickstart(SITE, '/', c.SITE_CONFIG)
