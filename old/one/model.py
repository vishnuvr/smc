"""
Workspace Server Database Model
"""

db_file = 'model.sqlite3'

import datetime, os

from sqlalchemy import create_engine
engine = create_engine('sqlite:///%s'%db_file)

from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

from sqlalchemy import (Boolean, Column, DateTime, Integer, String, ForeignKey)
from sqlalchemy.orm import relation, backref

class Port(Base):
    """
    EXAMPLES::

        >>> drop_all(); create()
        >>> S = session()
        >>> p = Port('frontend', 5000)    
        >>> p
        <model.Port object at...>
        >>> S.add(p)
        >>> S.add(Port('subprocess_server', 4999))
        >>> S.commit()
        >>> [(x.server, x.port) for x in S.query(Port).all()]
        [(u'frontend', 5000), (u'subprocess_server', 4999)]
    """
    __tablename__ = "ports"
    server = Column(String, primary_key=True)
    port = Column(Integer)

    def __init__(self, server, port):
        self.server = str(server)
        self.port = int(port)

class Session(Base):
    """
    EXAMPLES::
    
        >>> drop_all(); create()
        >>> s = Session(0, 12345, '/tmp/', 'http://localhost:5000'); s
        Session(0, pid=12345, path='/tmp/', url='http://localhost:5000', status='ready', next_cell_id=0, last_active_cell_id=-1, start_time=...)
    """
    __tablename__ = 'sessions'
    id = Column(Integer, primary_key=True)
    pid = Column(Integer)
    path = Column(String)
    url = Column(String)
    status = Column(String)
    next_cell_id = Column(Integer)
    last_active_cell_id = Column(Integer)
    start_time = Column(DateTime)
    cells = relation("Cell", order_by="Cell.cell_id",
                     backref='session',
                     cascade='all, delete, delete-orphan',
                     lazy='dynamic')
    # NOTE: the lazy=dynamic above makes a *huge* difference in the
    # performance of the execute command in frontend.py!
    
    def __init__(self, id, pid, path, url, status='ready', next_cell_id=0, last_active_cell_id=-1):
        """
        INPUT:

        - ``id`` -- nonnegative integer; the id in the session
        - ``pid`` -- positive integer; the pid of the corresponding process
        - ``path`` -- string; where the session starts running
        - ``url`` -- string; the URL where the backend listens when in its WAIT state
        - ``status`` -- string; 'ready', 'running', 'dead'  TODO: enforce this here and in setter!
        - ``next_cell_id`` -- the id that will be assigned to the next cell that is evaluated
        - ``last_active_cell_id`` -- id of last cell that was submitted for evaluation
        """
        self.id = int(id)
        self.pid = int(pid)
        self.path = str(path)
        self.url = str(url)
        self.status = str(status)
        self.next_cell_id = int(next_cell_id)  # 
        self.last_active_cell_id = int(last_active_cell_id)  #
        self.start_time = datetime.datetime.now()

    def to_json(self):
        """
        Return a dictionary representation of this database object,
        which can be jsonify'd.

        EXAMPLES::

            >>> drop_all(); create()
            >>> s = Session(0, 12345, '/tmp/', 'http://localhost:5000')

        The output is a dict, with random key order, which is why this test is funny::
        
            >>> s.to_json()
            {...}
            >>> list(sorted(list(s.to_json().iteritems())))
            [('id', 0), ('last_active_cell_id', -1), ('next_cell_id', 0), ('path', '/tmp/'), ('pid', 12345), ('start_time', '...'), ('status', 'ready'), ('url', 'http://localhost:5000')]

        Confirm jsonifiability::
        
            >>> import json; json.dumps(s.to_json())
            '{...}'
        """
        return {'id':self.id, 'pid':self.pid, 'path':self.path,
                'url':self.url, 'status':self.status,
                'next_cell_id':self.next_cell_id,
                'last_active_cell_id':self.last_active_cell_id,
                'start_time':str(self.start_time)}

    def __repr__(self):
        """
        EXAMPLES::

            >>> drop_all(); create()
            >>> s = Session(0, 12345, '/tmp/', 'http://localhost:5000')
            >>> s.__repr__()
            "Session(0, pid=12345, path='/tmp/', url='http://localhost:5000', status='ready', next_cell_id=0, last_active_cell_id=-1, start_time=...)"
        """
        return "Session(%s, pid=%s, path='%s', url='%s', status='%s', next_cell_id=%s, last_active_cell_id=%s, start_time=%s)"%(
            self.id, self.pid, self.path, self.url, self.status,
            self.next_cell_id, self.last_active_cell_id, self.start_time)

class Cell(Base):
    """
    EXAMPLES::

        >>> drop_all(); create()
        >>> s = Session(0, 12345, '/tmp/', 'http://localhost:5000')
        >>> c = Cell(0, 0, 'print(2+3)'); c
        Cell(0, session_id=0, code='print(2+3)', output=[])
    """
    __tablename__ = 'cells'
    cell_id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey('sessions.id'), primary_key=True)
    code = Column(String)
    output = relation("OutputMsg", order_by="OutputMsg.number",
                      backref='cell',
                      cascade='all, delete, delete-orphan',
                      primaryjoin='and_(Cell.session_id==OutputMsg.session_id, Cell.cell_id==OutputMsg.cell_id)')

    def __init__(self, cell_id, session_id, code):
        """
        INPUT:

        - ``cell_id`` -- nonnegative integer
        - ``session_id`` -- nonnegative integer
        - ``code`` -- string
        """
        # TODO: enforce constraints
        self.cell_id = int(cell_id)
        self.session_id = int(session_id)
        self.code = str(code)

    def to_json(self):
        """
        Return a dictionary representation of this database object,
        which can be jsonify'd.

        EXAMPLES::

            >>> drop_all(); create()
            >>> s = Session(0, 12345, '/tmp/', 'http://localhost:5000')
            >>> c = Cell(0, 0, 'print(2+3)')
            >>> c.to_json()
            {...}
            >>> list(sorted(list(c.to_json().iteritems())))
            [('cell_id', 0), ('code', 'print(2+3)')]

        Confirm jsonifiability::
        
            >>> import json; json.dumps(c.to_json())
            '{...}'
        

        """
        return {'cell_id':self.cell_id, 'code':self.code}

    def __repr__(self):
        """
        EXAMPLES::
        
            >>> drop_all(); create()
            >>> s = Session(0, 12345, '/tmp/', 'http://localhost:5000')
            >>> c = Cell(0, 0, 'print(2+3)')
            >>> c.__repr__()
            "Cell(0, session_id=0, code='print(2+3)', output=[])"
        """
        return "Cell(%s, session_id=%s, code='%s', output=%s)"%(
            self.cell_id, self.session_id, self.code, self.output)

class OutputMsg(Base):
    """
    EXAMPLES::

        >>> drop_all(); create()
        >>> s = Session(0, 12345, '/tmp/', 'http://localhost:5000')
        >>> c = Cell(0, 0, 'print(2+3)')
        >>> o = OutputMsg(0, 0, 0); o
        OutputMsg(0, cell_id=0, session_id=0, done=None, output='None', modified_files='None')
    """
    __tablename__ = 'output_msg'
    number = Column(Integer, primary_key=True)
    cell_id = Column(Integer, ForeignKey('cells.cell_id'), primary_key=True)
    session_id = Column(Integer, ForeignKey('cells.session_id'), primary_key=True)
    done = Column(Boolean)
    output = Column(String)
    modified_files = Column(String)

    def __init__(self, number, cell_id, session_id):
        """
        Create an OutputMsg object.

        INPUT:

        - ``number`` -- (nonnegative integer) message number
        - ``cell_id`` -- (nonnegative integer) id of block of code
          that is being evaluated
        - ``session_id`` -- (nonnegative integer) id of session in
          which code is being evaluated
        """
        self.number = int(number)
        self.cell_id = int(cell_id)
        self.session_id = int(session_id)

    def __repr__(self):
        """
        EXAMPLES::

            >>> drop_all(); create()
            >>> s = Session(0, 389, '/tmp/', 'http://localhost:54321')
            >>> c = Cell(0, 0, 'print(3+8+9)')
            >>> o = OutputMsg(0, 0, 0); o.__repr__()
            "OutputMsg(0, cell_id=0, session_id=0, done=None, output='None', modified_files='None')"
            >>> o.done = True; o.output = '20'; o.modified_files = ''
            >>> o.__repr__()
            "OutputMsg(0, cell_id=0, session_id=0, done=True, output='20', modified_files='')"
        """
        return "OutputMsg(%s, cell_id=%s, session_id=%s, done=%s, output='%s', modified_files='%s')"%(
            self.number, self.cell_id, self.session_id, self.done,
            self.output, self.modified_files)

def drop_all():
    r"""
    Delete everything from the database.

    EXAMPLES::

    We delete everything, create the DB again, enter a record, confirm
    it is there, then delete everything, and confirm the record is
    gone::

        >>> drop_all()
        >>> create()
        >>> S = session()
        >>> S.add(Session(0, 12345, '/tmp/', 'http://localhost:5000'))
        >>> S.commit()
        >>> S.query(Session).count()
        1
        >>> drop_all()
        >>> S = session()

    This query fails because we deleted all the tables::
    
        >>> S.query(Session).count()
        Traceback (most recent call last):
        ...
        OperationalError: (OperationalError) no such table...
    """
    Base.metadata.drop_all(engine)

def session():
    """
    Return a database session.
    
    EXAMPLES::

        >>> session()
        <sqlalchemy.orm.session.Session...>
    """
    from sqlalchemy.orm import sessionmaker
    Session = sessionmaker(bind=engine)
    return Session()

def create():
    r"""
    Create the database.

    EXAMPLES::

    We first do a query before the database is created and get an
    error::

        >>> drop_all()
        >>> S = session()
        >>> S.query(Session).count()
        Traceback (most recent call last):
        ...
        OperationalError: (OperationalError) no such table...

    After creating the DB, it works, and we get no records::

        >>> create()
        >>> S.query(Session).count()
        0
    """
    Base.metadata.create_all(engine)



