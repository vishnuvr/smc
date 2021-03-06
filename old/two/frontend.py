"""
Frontend

"""

import os, socket

##########################################################
# Setup logging
##########################################################
import logging
log = logging.getLogger()

##########################################################
# The database
##########################################################
import frontend_database_sqlalchemy as db

##########################################################
# Managing workers
##########################################################

class WorkerManager(object):
    def list_all(self):
        return [{'id':b.id, 'backend_id':b.backend_id,
                 'account':b.account,
                 'timestamp':db.timestamp_to_str(b.timestamp)}
                for b in db.session().query(db.Worker)]

    def add(self, data):
        try:
            s = db.session()
            for x in data.splitlines():
                z = {}
                for w in x.split(','):
                    key, value = w.split('=')
                    z[key.strip()] = value.strip()
                worker = db.Worker(hostname=z['account'])
                try:
                    backend = s.query(db.Backend).filter(db.Backend.id == int(z['backend_id'])).one()
                except:
                    raise RuntimeError, "unknown backend id number %s"%z['backend_id']
                backend.workers.append(worker)
            s.commit()
            return {'status':'ok'}
        except Exception, msg:
            return {'status':'error', 'mesg':str(msg)}

    def delete(self, data):
        try:
            s = db.session()
            for x in data.split(','):
                key, value = x.split('=')
                if key != 'id':
                    raise ValueError, "format must be id="
                value = int(value)
                try:
                    s.delete(s.query(db.Worker).filter(db.Worker.id == value).one())
                except:
                    raise RuntimeError, "unknown worker id number %s"%value
            s.commit()
        except Exception, msg:
            return {'status':'error', 'mesg':str(msg)}


worker_manager = WorkerManager()        

##########################################################
# Managing backends
##########################################################

class BackendManager(object):
    def status_update(self, id, status):
        try:
            s = db.session()
            b = s.query(db.Backend).filter(db.Backend.id == id).one()
            b.status = status
            db.stamp(b)
            s.commit()
            return {'status':'ok'}
        except Exception, m:
            return {'status':'error', 'mesg':str(m)}
        
    def list_all(self):
        return [{'id':b.id,
                 'URI':b.URI,
                 'user':b.user,
                 'debug':b.debug,
                 'path':b.path,
                 'workers':len(b.workers),
                 'status':b.status,
                 'load_number':b.load_number,
                 'number_of_connected_users':b.number_of_connected_users,
                 'number_of_stored_workspaces':b.number_of_stored_workspaces,
                 'disk_usage':b.disk_usage,
                 'disk_available':b.disk_available}
                for b in db.session().query(db.Backend)]

    def add(self, lines):
        if lines:
            # there are lines to add
            try:
                s = db.session()
                for line in lines.splitlines():
                    if line.strip():
                        URI, user, path = line.split()
                        b = db.Backend()
                        b.URI = URI; b.user = user; b.path = path; b.status = 'stopped'; 
                        s.add(b)
                s.commit()
                return {'status':'ok'}
            except Exception, mesg:
                return {'status':'error', 'mesg':str(mesg)}

    def backend_cmd(self, backend, extra_args=''):
        URI = backend.URI.lower()
        i = URI.find('://')
        v = URI[i+3:].split(':')
        host = v[0]
        if len(v) == 1:
            port = 80 if URI.startswith('http://') else 443
        else:
            port = v[1]
        user = backend.user
        if user is None:
            import getpass
            user = getpass.getuser()
        debug = backend.debug
        path = backend.path
        workers = ','.join([w.hostname for w in backend.workers])

        backend_tag = 'backend%s'%backend.id

        # TODO: change to use subprocess.
        cmd = '''ssh "%s@%s" "cd '%s'&&exec ./sage -python backend.py %s --id=%s --workers=%s --port=%s --frontend=%s %s %s >stdout.log 2>stderr.log &"'''%(
            user, host, path, '--debug' if debug else '',
            backend.id, workers, port, frontend_URI(),
            '--log=%s --log_tag=%s'%(logger_url, backend_tag) if args.log else '',
            extra_args)
        log.debug(cmd)

        return cmd
        
    def start(self, id):
        try:
            s = db.session()
            b = s.query(db.Backend).filter(db.Backend.id==id).one()
            if b.status == 'running':
                # nothing to do
                pass
            else:
                b.status = 'starting'
                s.commit()
                cmd = self.backend_cmd(b)
                log.debug(os.popen(cmd).read())
                log.debug("command sent")                
            return {'status':'ok'}
        except Exception, mesg:
            print mesg # todo
            return {'status':'error', 'mesg':str(mesg)}

    def stop(self, id):
        try:
            s = db.session()
            b = s.query(db.Backend).filter(db.Backend.id==id).one()
            b.status = 'stopping'
            s.commit()
            cmd = self.backend_cmd(b, extra_args="--stop=True")
            log.debug(os.popen(cmd).read())
            log.debug("command sent")
            return {'status':'ok'}
        except Exception, mesg:
            print mesg
            return {'status':'error', 'mesg':str(mesg)}

    def start_all(self):
        s = db.session()
        ids = [b.id for b in s.query(db.Backend).filter(db.Backend.status == 'stopped')]
        bad = []
        for id in ids:
            mesg = self.start(id)
            if mesg['status'] == 'error':
                bad.append(id)
        if bad:
            return {'status':'error', 'bad':bad}
        else:
            return {'status':'ok'}

    def stop_all(self):
        s = db.session()
        ids = [b.id for b in s.query(db.Backend).filter(db.Backend.status == 'running')]
        bad = []
        for id in ids:
            mesg = self.stop(id)
            if mesg['status'] == 'error':
                bad.append(id)
        if bad:
            return {'status':'error', 'bad':bad}
        else:
            return {'status':'ok'}

        
    def delete(self, id):
        try:
            s = db.session()
            for wl in s.query(db.WorkspaceLocation).filter(db.WorkspaceLocation.backend_id==id):
                s.delete(wl)
            for b in s.query(db.Backend).filter(db.Backend.id==id):
                s.delete(b)
            s.commit()
            return {'status':'ok'}
        except Exception, mesg:
            return {'status': 'error', 'mesg':str(mesg)}


backend_manager = BackendManager()        


##########################################################
##########################################################
##
##   Web server
##
##########################################################
##########################################################

import json
from tornado import web, ioloop

routes = []


##########################################################
# Backend <--> Frontend registration, etc. 
##########################################################
class BackendStatusUpdateHandler(web.RequestHandler):
    def post(self):
        self.write(json.dumps(backend_manager.status_update(
            self.get_argument('id'), self.get_argument('status'))))

routes.extend([
    (r"/backend/send_status_update", BackendStatusUpdateHandler),
    ])

##########################################################
# Web server: Management Console Interface
##########################################################

class ManageHandler(web.RequestHandler):
    def get(self):
        self.render('static/sagews/desktop/manage.html')

# Backends
class ManageBackendsListAllHandler(web.RequestHandler):
    def get(self):
        self.write(json.dumps(backend_manager.list_all()))

class ManageBackendsAddHandler(web.RequestHandler):
    def post(self):
        self.write(json.dumps(backend_manager.add(self.get_argument('data').strip())))

class ManageBackendsDeleteHandler(web.RequestHandler):
    def post(self):
        self.write(json.dumps(backend_manager.delete(self.get_argument('id'))))

class ManageBackendsStartHandler(web.RequestHandler):
    def post(self):
        self.write(json.dumps(backend_manager.start(self.get_argument('id'))))

class ManageBackendsStopHandler(web.RequestHandler):
    def post(self):
        self.write(json.dumps(backend_manager.stop(self.get_argument('id'))))

class ManageBackendsStartAllHandler(web.RequestHandler):
    def post(self):
        self.write(json.dumps(backend_manager.start_all()))

class ManageBackendsStopAllHandler(web.RequestHandler):
    def post(self):
        self.write(json.dumps(backend_manager.stop_all()))


# Workers
class ManageWorkersListAllHandler(web.RequestHandler):
    def get(self):
        self.write(json.dumps(worker_manager.list_all()))

class ManageWorkersAddHandler(web.RequestHandler):
    def post(self):
        self.write(json.dumps(worker_manager.add(self.get_argument('data').strip())))

class ManageWorkersDeleteHandler(web.RequestHandler):
    def post(self):
        self.write(json.dumps(worker_manager.delete(self.get_argument('data').strip())))

routes.extend([
    (r"/manage", ManageHandler),
    
    (r"/manage/backends/list_all", ManageBackendsListAllHandler),
    (r"/manage/backends/add", ManageBackendsAddHandler),    
    (r"/manage/backends/delete", ManageBackendsDeleteHandler),
    (r"/manage/backends/start", ManageBackendsStartHandler),    
    (r"/manage/backends/stop", ManageBackendsStopHandler),
    (r"/manage/backends/start_all", ManageBackendsStartAllHandler),    
    (r"/manage/backends/stop_all", ManageBackendsStopAllHandler),

    (r"/manage/workers/list_all", ManageWorkersListAllHandler),
    (r"/manage/workers/add", ManageWorkersAddHandler),    
    (r"/manage/workers/delete", ManageWorkersDeleteHandler),
    
    (r"/static/(.*)", web.StaticFileHandler, {'path':'static'})
])

##########################################################
# Web server: Launch it
##########################################################

def run(port, address, debug, secure):
    print "Launching frontend%s: %s"%(
        ' in debug mode' if debug else ' in production mode',
        frontend_URI())

    if debug:
        log.setLevel(logging.DEBUG)

    if secure:  # todo
        raise NotImplementedError
    
    app = web.Application(routes, debug=debug)
    app.listen(port=port, address=address)
    ioloop.IOLoop.instance().start()

def frontend_URI():
    import socket
    return 'http%s://%s:%s'%(
        's' if args.secure else '',
        args.external, args.port)

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description="Run a frontend instance")
    parser.add_argument("--port", "-p", dest='port', type=int, default=8080,
                        help="port the frontend listens on (default: 8080)")
    parser.add_argument("--address", "-a", dest="address", type=str, default="",
                        help="address the frontend listens on (default: ''=everything)")
    parser.add_argument("--external", dest="external", type=str, default="",
                        help="address backends use to communicate with frontend (default: socket.gethostname())")
    parser.add_argument("--debug", "-d", dest="debug", action='store_const', const=True,
                        help="debug mode (default: False)", default=False)
    parser.add_argument("--secure", "-s", dest="secure", action='store_const', const=True,
                        help="SSL secure mode (default: False)", default=False)
    
    parser.add_argument("--log", dest="log", type=str, default="",
                        help="if specified use secure remote log server at that location (e.g., 'localhost:9020')")
    parser.add_argument("--log_tag", dest="log_tag", type=str, default="",
                        help="tag to include in log messages, which could be used to identify this process, e.g., 'backend7'")
    args = parser.parse_args()

    if args.log:
        from log import TornadoLogHandler
        log.addHandler(TornadoLogHandler(address=args.log, tag=args.log_tag))

    if not args.external:        
        args.external = args.address if args.address else socket.gethostname()
        
    run(args.port, args.address, args.debug, args.secure)


