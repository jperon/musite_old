#!/usr/bin/env python3
import os,sys,re
from string import Template
sys.path.insert(0, './etc')
sys.path.insert(0, './lib')
sys.path.insert(0, './lib/plugins')
import cherrypy as cp
import config
import auth as a, outils as s

PLUGINS = {}
for m in config.PLUGINS: PLUGINS[m] = __import__(m)
PWD = os.path.abspath(os.getcwd())

def presenter(retourner,plugin):
    '''Chargement des plugins.'''
    @cp.expose
    def retour(*arguments,**parametres):
        cp.session['plugin'] = plugin
        return retourner(*arguments,**parametres)
    return retour

class Site:
    '''Cœur du site : chaque méthode décorée par cherrypy.expose
    correspond à une page du site.'''
    @cp.expose
    @s.page
    def index(self):
        '''Page d'accueil.'''
        with open('lib/index.html','r') as f:
            return f.read(-1)
    @cp.expose
    def css(self):
        '''Feuille de styles.'''
        with open(os.path.join('modeles','style.css')) as f: css = Template(f.read(-1))
        try:
            plugin = PLUGINS[cp.session['plugin']].CSS
        except (AttributeError,KeyError):
            plugin = ''
        return css.substitute(plugin = plugin)

class Admin():
    @cp.expose
    @s.page
    @a.reserver(groupe='admin')
    def index(self):
        return 'Bonjour, {0} !'.format(cp.request.login)
    @cp.expose
    @s.page
    @a.reserver(utilisateur='admin')
    def utilisateurs(self):
        return '<br>'.join([u for u in a.utilisateurs().keys()])

if __name__ == '__main__':
    config.SERVER_CONFIG

    site_config = {
         '/': {
             'tools.sessions.on': True,
             'tools.staticdir.root': PWD
             },
         '/static': {
             'tools.staticdir.on': True,
             'tools.staticdir.dir': './static'
             },
        }

    site = Site()
    for m in PLUGINS.keys():
        site_config[m] = {'tools.sessions.on':True}
        setattr(site,m,presenter(PLUGINS[m].retourner,m))
    site.admin = Admin()

    cp.config.update(config.SERVER_CONFIG)
    cp.quickstart(site, '/', site_config)
