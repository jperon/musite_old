import os
from string import Template
import config as c

def page(fonction):
    def afficher(*arguments,**parametres):
        with open(os.path.join('modeles','page.html')) as f: page = Template(f.read(-1))
        index = ('<b>Pages</b><ul>\n'
            + '\n'.join(['<li plain=true><a href=/{0}/>{0}</a></li>'.format(plugin) for plugin in c.PLUGINS])
            + '\n</ul>'
            + '<b><a href="/admin/">Admin</a></b><ul>\n'
            + '<a href="/admin/utilisateurs">utilisateurs</a></ul>\n'
            )
        return page.substitute(
                    titre = c.TITRE,
                    index = index,
                    corps = fonction(*arguments,**parametres),
                    )
    return afficher
