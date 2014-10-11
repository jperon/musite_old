#!/usr/bin/env python3
import os,sys,re
from string import Template
sys.path.insert(0, './etc')
sys.path.insert(0, './lib')
sys.path.insert(0, './lib/plugins')
import cherrypy
import config
import auth as a, outils as s

PLUGINS = {}
for m in config.PLUGINS: PLUGINS[m] = __import__(m)

PWD = os.path.abspath(os.getcwd())

def presenter(accueillir,plugin):
    '''Chargement des plugins.'''
    def retour(*arguments,**parametres):
        cherrypy.session['plugin'] = plugin
        return str(s.Page(accueillir(*arguments,**parametres)))
    return retour

class Site:
    '''Cœur du site : chaque méthode décorée par cherrypy.expose
    correspond à une page du site.'''
    @cherrypy.expose
    def index(self):
        '''Page d'accueil.'''
        with open('lib/index.html','r') as f:
            return s.Page(f.read(-1)).contenu
    @cherrypy.expose
    @cherrypy.expose
    def css(self):
        '''Feuille de styles.'''
        with open(os.path.join('modeles','style.css')) as f: css = Template(f.read(-1))
        try:
            plugin = PLUGINS[cherrypy.session['plugin']].CSS
        except (AttributeError,KeyError):
            plugin = ''
        return css.substitute(plugin = plugin)

class Admin():
    @cherrypy.expose
    @a.reserver(groupe='admin')
    def index(self):
        return str(s.Page('Bonjour, {0} !'.format(cherrypy.request.login)))
    @cherrypy.expose
    @a.reserver(utilisateur='admin')
    def utilisateurs(self):
        return str(s.Page('<br>'.join([u for u in utilisateurs().keys()])))

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
        setattr(site,m,cherrypy.expose(presenter(PLUGINS[m].accueillir,m)))
    site.admin = Admin()

    cherrypy.config.update(config.SERVER_CONFIG)
    cherrypy.quickstart(site, '/', site_config)
