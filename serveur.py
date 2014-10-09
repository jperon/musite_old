#!/usr/bin/env python3
import os,sys,re,hashlib
from string import Template
sys.path.insert(0, './etc')
sys.path.insert(0, './lib')
sys.path.insert(0, './lib/plugins')
import config
import cherrypy

PLUGINS = {}
for m in config.PLUGINS: PLUGINS[m] = __import__(m)

PWD = os.path.abspath(os.getcwd())

class Site:
    @cherrypy.expose
    def index(self):
        with open('lib/index.html','r') as f:
            return Page(f.read(-1)).contenu
    @cherrypy.expose
    def css(self):
        with open(os.path.join('modeles','style.css')) as f: css = Template(f.read(-1))
        try:
            plugin = PLUGINS[cherrypy.session['plugin']].CSS
        except (AttributeError,KeyError):
            plugin = ''
        return css.substitute(plugin = plugin)

def presenter(accueillir,plugin):
    def retour(*arguments,**parametres):
        cherrypy.session['plugin'] = plugin
        return Page(accueillir(*arguments,**parametres)).contenu
    return retour


def admin():
    return Page('Accès réservé.').contenu


class Page:
    def __init__(self,corps):
        with open(os.path.join('modeles','page.html')) as f: self.page = Template(f.read(-1))
        self.index = ('<b>Pages</b><ul>\n'
            + '\n'.join(['<li plain=true><a href=/{0}/>{0}</a></li>'.format(plugin) for plugin in config.PLUGINS])
            + '\n</ul>'
            + '<b><a href="/admin/">Admin</a></b>'
            )
        self.corps = corps
    @property
    def contenu(self):
        return self.page.substitute(
                            titre = config.TITRE,
                            index = self.index,
                            corps = self.corps,
                            )

def users():
    return {'admin':'d033e22ae348aeb5660fc2140aec35850c4da997'}

def encrypt_pw(pw):
    pw = pw.encode('utf-8')
    return hashlib.sha1(pw).hexdigest()

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
         '/admin': {
             'tools.basic_auth.on': True,
             'tools.basic_auth.realm': 'Accès réservé',
             'tools.basic_auth.users': users,
             'tools.basic_auth.encrypt': encrypt_pw
             }
        }

    site = Site()
    for m in PLUGINS.keys():
        site_config[m] = {'tools.sessions.on':True}
        setattr(site,m,cherrypy.expose(presenter(PLUGINS[m].accueillir,m)))
    site.admin = cherrypy.expose(admin)

    cherrypy.config.update(config.SERVER_CONFIG)
    cherrypy.quickstart(site, '/', site_config)
