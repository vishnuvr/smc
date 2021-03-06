



---
The options:

- store highly compressed backup of project (with internal rsnapshot) in cassandra, but there will *always* be a copy of the project extracted on some machine, which is needed for people to browse it.

or

- have numerous copies of all projects with nginx pointed out them.

or both, but with just one static copy, somehow organized... (?) at some point someday.


---

# Deployment Plan -- what do we need in place?

This is pretty neat -- this should be how cloud starts -- just have a worksheet, and have it suck you into more:

This is also a sketch of our architecture:

    http://sketchboard.me/Xydh8wrYRCtR

- each project is stored as a sequence of highly compressed blobs in the database
- we use tar to store only modified files

- storage of each user project somehow, either on FS or in database -- DATABASE.
- modify admin.py config to properly set these (from data/local/cassandra/cassandra.yaml) to be large:
    thrift_framed_transport_size_in_mb: 1500
    thrift_max_message_length_in_mb: 1600

- I tried using "xz" compression on `node_modules`, as a test:

time tar -cf - node_modules | xz -9 -c - > foo.tar.xz

It is only 5MB (20 seconds) versus 8.4MB (6 seconds) using "tar jcf".
The original directory is 52MB.

Try storing as a blob:

- multiple hubs
- cassandra deployed on multiple machines
- backup of cassandra database (?)
- redirect of cloud.sagemath.org (non-secure version)

- easy way to upgrade everything, including forcing restart of localhubs:
   -- push out new static code to 4 locations (for now).
   -- update a ver



After first deploy, top priority, in order:

* (0:30?) [ ] REMOVE: worksheet1.html -- why is it there?
* (0:45?) [ ] BUG: terminal paste doesn't work, usually
* (0:45?) [ ] BUG: 1-line terminal copy doesn't work, usually
* (1:00?) [ ] FEATURE: changing the syntax highlighting modes in codemirror automatically for percent modes.  And have a palette of percent modes.
* (0:15?) [ ] REMOVE: about.html and commented out stuff in `top_navbar`, assuming I really want to combine with help.
* (1:00?) [ ] BUG: fix/implement the open file tab resize code.
* (0:30?) [ ] FEATURE: donation link
* (1:00?) [ ] FEATURE: way user can self-report that they donated, how much, and when; stored in a "donations" table?

* (5:00?) [ ] FEATURE: consider swapping out term.js for hterm: https://github.com/macton/hterm


- (3:00?) [ ] upgrade haproxy and get rid of using stunnel.  This tutorial looks helpful:
        http://blog.exceliance.fr/2012/09/10/how-to-get-ssl-with-haproxy-getting-rid-of-stunnel-stud-nginx-or-pound/
Maybe as easy as this:
              bind :443 ssl crt /etc/haproxy/site.pem

---------------------------------------

- [ ] idea -- html5 audio: http://www.html5rocks.com/en/tutorials/webaudio/intro/





(1:00?) [ ] "Any decent text editor should make email-style quoting easy. For example, with BBEdit, you can make a selection and choose Increase Quote Level from the Text menu."  (from markdown definition)

(1:00?) [ ] delete trailing whitespace and cursors -- instead of avoiding the line where there is a cursor, when applying a diff, put trailing whitespace back in, so that cursor moves to where it should.  This is a much better approach.


[ ] worksheet zoom mode -- need something for PRESENTATIONS -- zooming the browser is useless.

(2:00?) [ ] editor/worksheet/terminal -- fullscreen mode for each, esp. worksheet, since that is needed for presentations.

(1:00?) [ ] worksheet -- section toggle status needs to be preserved.

(1:00?) [ ] worksheet -- export to html mode (?)

(2:00?) [ ] add a markdown preview mode to the editor -- generic preview modes would be good...

(6:00?) [ ] 3d graphics using three.js -- this is CRITICAL in order to use SMC in my math 308 teaching!

(0:30?) [ ] it is possible to drag documentation out of the window
    and then impossible to bring it back!

(0:30?) [ ] var('x','y') is supposed to work according to docs, but I
    screwed it up.

(1:00?) [ ] BUG terminal -- sometimes it freezes and you have to open/close it.

(0:30?) [ ] the current path html wraps way too skinny -- make a long path and see.
(0:30?) [ ] filename in terminal wraps way too early -- should cut off beginning, not end.

(1:00?) [ ] I had to open/close a file since it got "stuck" in "syncing" -- this should be made even more robust.

(1:00?) [ ] download from web link will need some intelligence, e.g., how to handle github links.

(0:30?) [ ] worksheet load -- better graphics, esp if it will take a while.


(1:00?) [ ] some way to copy a file (e.g., a button the right that makes a copy with a similar name)

(0:30?) [ ] shift-enter in any contenteditable to submit.

(3:00?) [ ] split view mode for worksheets, just like for editor.  Could just initially use sync...

(0:30?) [ ] if worksheet starts with a section, no way to insert a cell above the section.

(1:00?) [ ] write new email validation and stop using validator, or figure out why it isn't working with browserify.  See client.coffee.

(0:30?) [ ] section deletion -- UI: delete title and it goes away.


(2:00?) [ ] console -- make it so the dang thing always gets focus!

(1:00?) [ ] feature -- save button should tell if *anybody* has made a change.

(0:30?) [ ] bug -- stopwatch is appearing where it shouldn't when making NESTED interacts.

[ ] BUG/issue -- terminal console resize doesn't work with node
    0.10.2, but does with 0.8.22, so I'm stuck with 0.8.22 for the
    client local_hub for now.  No older pty.js's work in 0.10.2.

publication:
(0:15?) [ ] ui -- under settings, give a link that brings up the project/file: https://cloud.sagemath.org/projects/project_id/path/in/filesystem
(0:40?) [ ] hub -- when user does a get on url for project/file, send message opening that project.


implement explorer:
---------------------
(0:20?) [ ] message: give me list of n projects with title/desc satisfying a query
(0:10?) [ ] ui -- box in which to type query
(0:20?) [ ] ui -- div/list in which to show results and click
(0:15?) [ ] ui readonly -- grey out plus to create file, settings
(0:15?) [ ] ui readonly -- codemirror edit sessions; sets the editor to readonly
(0:15?) [ ] ui readonly -- worksheets read only view (but still see)
(0:15?) [ ] ui readonly -- console read only view (but still see)



project sharing:
-----------------
(0:10?) [ ] message: add user to project
(0:10?) [ ] message: remove user from project
(0:20?) [ ] message: get all users by username; support in hub via db query; returns first/last/account_id that match.
(0:15?) [ ] ui -- search for other users by login name
(0:20?) [ ] ui -- display other user names in a clickable scrollable list
(0:20?) [ ] ui -- display closeable pills representing users that who have invites access
(0:20?) [ ] ui -- remove self from project (if last, this deletes projects)


-------------

(0:45?) [ ] rsnapshot on the virtual machine, for local file recover -- how to easily configure and make available?


(3:00?)   [ ] arbitrary user-specified project location

(0:30?)   [ ] browserify issue

(1:00?)  [ ] editor -- ability to set the syntax highlight mode of a file

(0:45?)  [ ] bug -- if editing file with long name, vertical size is miscomputed. (I put in a 5-minute hack truncate.)
(0:30?)  [ ] make sure email reset works with cloud.sagemath.org
(1:00?)  [ ] worksheet: be able to print a worksheet (something involving HTML/CSS)

(3:00?)  [ ] worksheet pages: would make worksheets dramatically more scalable.



(1:00?)  [ ] MINIFY actual page js

(1:00?)  [ ] feature -- file browser listing pagination

(1:00?) [ ] ui idea -- it would be nice to mark the active editor tabs when there is activity in them.

(1:00?) [ ] bug -- when view split, history isn't shared, which is CONFUSING; maybe has something to do with syncdoc since option is set correctly.  Not sure.


(0:45?)  [ ] Clone a project (under settings).

(1:00?)  [ ] When creating a new project, option to choose from a list of users if there is more than one user associated to an account.


(0:45?)  [ ] bug -- delete directory containing a file being edited -- save *appears* to work, but doesn't.
(0:20?)  [ ] bug -- download file with bad URL/failure gives useless error
(0:30?)  [ ] in sign-up: explain that service it currently donation-supported.
(0:45?)  [ ] in settings: ask for money and give link to donate to Sage foundation.
               provide a checkbox that says "I have donated."  When they check it, it changes to a big thanks!


(0:45?)  [ ] cells: move (control-arrow) should move all cells with checkbox checked.  (and control-arrow doesn't work on os x, right?)

(0:45?)  [ ] split document editing (see two parts of doc at once): http://codemirror.net/doc/manual.html#linkedDoc

(1:00?)  [ ] attach: implement the attach command for (backwards) compatibility.
(1:00?)  [ ] option to completely delete a project, irrevocably.   (BIG RED SCARY SERIOUS -- type your name, etc.)

(0:30?)  [ ] show quota info in project settings.
(1:00?)  [ ] make note cells be markdown with $'s for math.  Codemirror editor with syntax highlighting.


(0:30?)  [ ] codemirror editor settings: whether or not lines wrap in codemirror. (apply for both files and worksheets)  apply for both files and worksheets)apply for both files and worksheets)apply for both files and worksheets)apply for both files and worksheets)apply for both files and worksheets)apply for both files and worksheets)apply for both files and worksheets)
(0:20?)  [ ] codemirror editor settings: color scheme
(0:20?)  [ ] codemirror editor settings: auto delete trailing whitespace should be an option in global settings


(0:45?) [ ] sync: global hub needs to also timeout inactive sync sessions.




= Graphics =

(4:00x)    [ ] attempt very basic 3d rendering using three.js
(1:00?)  [ ] bug -- changing interact control externally does change control, but doesn't re-evaluate function.
@interact
def f(c=Color('blue'), thickness=(1..30)):
    show(plot(sin, color=c, thickness=thickness))
f.thickness=20

= Features =
(0:45?)  [ ] Editor bookmarks?.  Ctrl-B to toggle then, Ctrl-I to move to next?
(1:00x)  [ ] when a local_hub is starting, show a progress meter... (and sequence of messages)
(1:00?)  [ ] check multiple file and drag them in a group to move them.
(0:45?)  [ ] project rename/desc just like file rename

(2:00x)  [ ] write some basic user-oriented documentation (?)


(0:45?)  [ ] it might be nice if open file thing had -- in upper right -- "scratch: [ws] [trm]" icons...?
(0:45?)  [ ] close brackets -- would make editor and notebook nicer, maybe -- http://codemirror.net/addon/edit/closebrackets.js
(1:30?) [ ] Implement a simple "single cell" mode for visitor mode (basically, a sage session, but not using this project)
(1:30x) [ ] Implement a simple homework assignment mode for visitor mode, which lets user do problems, with results getting saved somewhere not-public.
(1:30?) [ ] For easy user-only recover of mistakes, setup rsnapshot
            on the same virtual machine, made with rsync,
            and way to browse it (symlink to path of project)
(1:30?) [ ] When a user logs in and accesses a project (if we haven't already in the last x
	       hours) do a compressed tarball backup of the project.
            Next time, only include files that were modified since the
            last backup by using the options mentioned here:
                http://catlingmindswipe.blogspot.com/2010/02/linux-how-to-incremental-backups-using.html
(1:30?) [ ] Make a new project from a specific backup of project.
             (just show list of times when there were backups made, and sizes)

(1:00?)  [ ] *need* to easily be able to resize the height of the output and have this saved!!!
(1:00?) [ ] A project-level chat, in addition to file level -- this gets stored in project_root/.sage-chat

Other issues

(1:00?) [ ] issue: if you open a #! script the first line isn't read until connecting to the sync session,
        so we don't have any way to know the file type... hence the codemirror editor doesn't have
        the right mode.


(1:00?)  [ ] informal terms of usage -- put up something very short but useful and serious.
(0:45?)  [ ] Do not allow creation of private projects unless users claims to have donated.
(1:00?)  [ ] provide a true 100% fullscreen mode for each editor, which covers everything...
(0:30?)  [ ] maybe nice if way to indicate which files (in recent) have unsaved changes??


(0:45?)  [ ] when searching, automatically copy highlighted text into search box.



-----

(1:00?) [ ] when a session has timed out, chat just doesn't work.
            typing once into the session and waiting... makes chat work.


Project =
   - Unix user
   - Sequence of tarballs stored in cassandra db
Each account will have a list of unix users associated to it, starting with *exactly one*.

A unix user = username@host... such that hub can ssh in.
Unix users can be shared with other users of SMC; if a user is shared, then both users of SMC have 100% access to everything.
Database table that lists all projects for a given user.
