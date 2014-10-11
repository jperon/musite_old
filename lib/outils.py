import os
from string import Template
import config

print(config.PLUGINS)

def page(fonction):
    def afficher(*arguments,**parametres):
        with open(os.path.join('modeles','page.html')) as f: page = Template(f.read(-1))
        index = ('<b>Pages</b><ul>\n'
            + '\n'.join(['<li plain=true><a href=/{0}/>{0}</a></li>'.format(plugin) for plugin in config.PLUGINS])
            + '\n</ul>'
            + '<b><a href="/admin/">Admin</a></b><ul>\n'
            + '<a href="/admin/utilisateurs">utilisateurs</a></ul>\n'
            )
        return page.substitute(
                    titre = config.TITRE,
                    index = index,
                    corps = fonction(*arguments,**parametres),
                    )
    return afficher

class Page:
    def __init__(self,corps):
        with open(os.path.join('modeles','page.html')) as f: self.page = Template(f.read(-1))
        self.index = ('<b>Pages</b><ul>\n'
            + '\n'.join(['<li plain=true><a href=/{0}/>{0}</a></li>'.format(plugin) for plugin in config.PLUGINS])
            + '\n</ul>'
            + '<b><a href="/admin/">Admin</a></b><ul>\n'
            + '<a href="/admin/utilisateurs">utilisateurs</a></ul>\n'
            )
        self.corps = corps
    @property
    def contenu(self):
        return self.page.substitute(
                            titre = config.TITRE,
                            index = self.index,
                            corps = self.corps,
                            )
    def __str__(self):
        return self.contenu
