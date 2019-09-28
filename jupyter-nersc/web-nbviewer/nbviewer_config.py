c.NBViewer.handler_settings    = {'clone_notebooks' : True}

c.NBViewer.local_handler       = "clonenotebooks.renderers.LocalRenderingHandler"
c.NBViewer.url_handler         = "clonenotebooks.renderers.URLRenderingHandler"
c.NBViewer.github_blob_handler = "clonenotebooks.renderers.GitHubBlobRenderingHandler"
c.NBViewer.github_tree_handler = "clonenotebooks.renderers.GitHubTreeRenderingHandler"
c.NBViewer.gist_handler        = "clonenotebooks.renderers.GistRenderingHandler"
c.NBViewer.user_gists_handler  = "clonenotebooks.renderers.UserGistsRenderingHandler"

c.NBViewer.localfiles = "/repos/nbviewer/notebook-5.7.8/tools/tests"
c.NBViewer.template_path = "/repos/clonenotebooks/templates"
