###############################################
# Matlab.py
# Part of Python-MATLAB-bridge
# Max Jaderberg 2012
###############################################
import urllib2, urllib, os, json

MATLAB_FOLDER = '%s/matlab' % os.path.realpath(os.path.dirname(__file__))

class Matlab(object):
    eval_func = 'web_feval.m'
    running = False

    def __init__(self, server='http://localhost', port=None, app_name='djmatlab'):
        self.server = '%s%s' % (server, ':%s' % port if port else '')
        self.app_name = app_name

    def is_connected(self):
        try:
            resp = self._open_page('test_connect.m', {'app_name': self.app_name})
            if resp['message']:
                return True
        except urllib2.URLError:
            pass
        return False

    def is_function_processor_working(self):
        try:
            result = self.run('%s/test_functions/test_sum.m' % MATLAB_FOLDER, {'echo': 'Matlab: Function processor is working!'})
            if result['success'] == 'true':
                return True
        except urllib2.URLError:
            pass
        return False

    def run(self, func_path, func_args=None, maxtime=None):
        page_args = {
            'func_path': func_path,
        }
        if func_args:
            page_args['arguments'] = json.dumps(func_args)
        if maxtime:
            result = self._open_page(self.eval_func, page_args, maxtime)
        else:
            result = self._open_page(self.eval_func, page_args)
        return result

    def _open_page(self, page_name, arguments={}, timeout=10):
        self.running = True
        page = urllib2.urlopen('%s/%s' % (self.server, page_name), urllib.urlencode(arguments), timeout)
        self.running = False
        return json.loads(page.read())


