#!/usr/bin/env python3
import os,sys,re
from string import Template
sys.path.insert(0, './lib')
sys.path.insert(0, './lib/plugins')
import config
import cherrypy

PLUGINS = {}
for m in config.PLUGINS: PLUGINS[m] = __import__(m)

PWD = os.path.abspath(os.getcwd())

class Site:
    exposed = True
    @cherrypy.tools.accept(media='text/html')
    @cherrypy.expose
    def GET(self,url='gregorio'):
        if url in PLUGINS:
            cherrypy.session['plugin'] = url
            page = Page(PLUGINS[cherrypy.session['plugin']].ACCUEIL)
            return page.contenu
        elif url == 'css': return self.css
        else: return Page('<p>404 : Il doit y avoir une erreur dans votre adresse…</p>').contenu
    @cherrypy.expose
    def POST(self,url='gregorio',texte=''):
        sortie = PLUGINS[cherrypy.session['plugin']].traiter(texte)
        os.renames(os.path.join(sortie['dossier'],sortie['fichier']),os.path.join('static','files',cherrypy.session['plugin'],sortie['fichier']))
        return Page(
            '<object type="application/pdf" data="/static/files/{0}/{1}" zoom="page" width="100%" height="100%"></object>'.format(
                cherrypy.session['plugin'],sortie['fichier']
                )
            ).contenu
    @property
    def css(self):
        with open(os.path.join('modeles','style.css')) as f: css = Template(f.read(-1))
        try:
            plugin = PLUGINS[cherrypy.session['plugin']].CSS
        except KeyError:
            plugin = ''
        return css.substitute(plugin = plugin)

class Page:
    def __init__(self,corps):
        with open(os.path.join('modeles','page.html')) as f: self.page = Template(f.read(-1))
        self.index = '<ul>\n' + '\n'.join(['<li plain=true><a href=/{0}>{0}</a></li>'.format(plugin) for plugin in config.PLUGINS]) + '\n</ul>'
        self.corps = corps
    @property
    def contenu(self):
        return self.page.substitute(
                            titre = config.TITRE,
                            index = self.index,
                            corps = self.corps,
                            )


if __name__ == '__main__':
    server_config={
        'server.socket_host': '0.0.0.0',
        'server.socket_port':2443,

        'server.ssl_module':'builtin',
        'server.ssl_certificate':'/etc/ssl/musite.pem',
        'server.ssl_private_key':'/etc/ssl/musite.pem',
        }

    site_config = {
         '/': {
             'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
             'tools.response_headers.on': True,
             'tools.response_headers.headers': [('Content-Type', 'text/html')],
             'tools.sessions.on': True,
             'tools.staticdir.root': PWD
         },
         '/static': {
             'tools.staticdir.on': True,
             'tools.staticdir.dir': './static'
         },
        }

#    cherrypy.config.update(server_config)
    cherrypy.quickstart(Site(), '/', site_config)
