###############################################################################
# Copyright (c) 2013, William Stein
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# The views and conclusions contained in the software and documentation are those
# of the authors and should not be interpreted as representing official policies,
# either expressed or implied, of the FreeBSD Project.
###############################################################################



import json
from uuid import uuid4
def uuid():
    return str(uuid4())


#######################################################
# Three.js based plotting
#######################################################

import sage_salvus

def show_3d_plot_using_threejs(p, **kwds):

    #container id to store scene
    id = uuid()
    obj_list = []

    def parse_obj(obj):
        model = []
        for item in obj.split("\n"):
            if "usemtl" in item:
                tmp = str(item.strip())
                tmp_list = {}
                try:
                    tmp_list = {"material_name":name,"face3":face3,"face4":face4,"face5":face5}
                    model.append(tmp_list)
                except (ValueError,UnboundLocalError):
                    pass
                face3 = []
                face4 = []
                face5 = []
                tmp_list = []
                name = tmp.split()[1]


            if "f" in item:
                tmp = str(item.strip())
                face_num = len(tmp.split())
                for t in tmp.split():
                    if(face_num ==4):
                        try:
                            face3.append(int(t))
                        except ValueError:
                            pass

                    elif(face_num ==6):
                        try:
                            face5.append(int(t))
                        except ValueError:
                            pass
                    else:
                        try:
                            face4.append(int(t))
                        except ValueError:
                            pass

        tmp_list = {"material_name":name,"face3":face3,"face4":face4,"face5":face5}
        model.append(tmp_list)

        return model


    def parse_texture(p):
        texture_dict = []
        textures = p.texture_set()
        for item in range(0,len(textures)):
            texture_pop = textures.pop()
            string = str(texture_pop)
            item = string.split("(")[1]
            name = item.split(",")[0]
            color = texture_pop.color
            tmp_dict = {"name":name,"color":color}
            texture_dict.append(tmp_dict)

        return texture_dict



    def get_color(name,texture_set):
        for item in range(0,len(texture_set)):
            if(texture_set[item]["name"] == name):
                color = texture_set[item]["color"]
                color_list = [color[0],color[1],color[2]]
                break
            else:
                color_list = []
        return color_list


    def parse_mtl(p):
        mtl = p.mtl_str()
        all_material = []
        for item in mtl.split("\n"):
            if "newmtl" in item:
                tmp = str(item.strip())
                tmp_list = []
                try:
                    texture_set = parse_texture(p)
                    color = get_color(name,texture_set)
                except (ValueError,UnboundLocalError):
                    pass
                try:
                    tmp_list = {"name":name,"ambient":ambient, "specular":specular, "diffuse":diffuse, "illum":illum_list[0],
                               "shininess":shininess_list[0],"opacity":opacity_diffuse[3],"color":color}
                    all_material.append(tmp_list)
                except (ValueError,UnboundLocalError):
                    pass

                ambient = []
                specular = []
                diffuse = []
                illum_list = []
                shininess_list = []
                opacity_list = []
                opacity_diffuse = []
                tmp_list = []
                name = tmp.split()[1]

            if "Ka" in item:
                tmp = str(item.strip())
                for t in tmp.split():
                    try:
                        ambient.append(float(t))
                    except ValueError:
                        pass

            if "Ks" in item:
                tmp = str(item.strip())
                for t in tmp.split():
                    try:
                        specular.append(float(t))
                    except ValueError:
                        pass

            if "Kd" in item:
                tmp = str(item.strip())
                for t in tmp.split():
                    try:
                        diffuse.append(float(t))
                    except ValueError:
                        pass

            if "illum" in item:
                tmp = str(item.strip())
                for t in tmp.split():
                    try:
                        illum_list.append(float(t))
                    except ValueError:
                        pass



            if "Ns" in item:
                tmp = str(item.strip())
                for t in tmp.split():
                    try:
                        shininess_list.append(float(t))
                    except ValueError:
                        pass

            if "d" in item:
                tmp = str(item.strip())
                for t in tmp.split():
                    try:
                        opacity_diffuse.append(float(t))
                    except ValueError:
                        pass

        try:
            color = list(p.all[0].texture.color.rgb())
        except (ValueError, AttributeError):
            pass

        try:
            texture_set = parse_texture(p)
            color = get_color(name,texture_set)
        except (ValueError, AttributeError):
            color = []
            #pass

        tmp_list = {"name":name,"ambient":ambient, "specular":specular, "diffuse":diffuse, "illum":illum_list[0],
                   "shininess":shininess_list[0],"opacity":opacity_diffuse[3],"color":color}
        all_material.append(tmp_list)

        return all_material



    def gs_parametric_plot3d(p):
        id =int(3)
        face_geometry = parse_obj(p.obj())
        material = parse_mtl(p)
        vertex_geometry = []
        obj  = p.obj()
        for item in obj.split("\n"):
            if "v" in item:
                tmp = str(item.strip())
                for t in tmp.split():
                    try:
                        vertex_geometry.append(float(t))
                    except ValueError:
                        pass
        myobj = {"face_geometry":face_geometry,"id":id,"vertex_geometry":vertex_geometry,"material":material}
        obj_list.append(myobj)

    def gs_text3d(p):
        id =int(2)
        text3d_sub_obj = p.all[0]
        text_content = text3d_sub_obj.string

        myobj = {"vertices":[],"faces":[],"normals":[],"colors":[],"text":text_content,"id":id}
        obj_list.append(myobj)



    def gs_combination(p):
        for x in p.all:
            options[str(type(x))](x)


    def gs_inner(p):
        if (str(type(p.all[0]))=="<class 'sage.plot.plot3d.base.TransformGroup'>"):
            gs_parametric_plot3d(p)
        else:
            options[str(type(p.all[0]))](p)


    options = {"<class 'sage.plot.plot3d.base.TransformGroup'>": gs_inner,
               "<type 'sage.plot.plot3d.parametric_surface.ParametricSurface'>": gs_parametric_plot3d,#gs_plot3d,
               "<type 'sage.plot.plot3d.implicit_surface.ImplicitSurface'>":gs_parametric_plot3d,#gs_implicit_plot3d,
               "<class 'sage.plot.plot3d.base.Graphics3dGroup'>": gs_combination,
               "<class 'sage.plot.plot3d.shapes2.Line'>": gs_parametric_plot3d,
               "<type 'sage.plot.plot3d.parametric_surface.ParametricSurface'>":gs_parametric_plot3d,#gs_plot3d,
               "<class 'sage.plot.plot3d.parametric_surface.MobiusStrip'>":gs_parametric_plot3d,#gs_plot3d,
               "<class 'sage.plot.plot3d.shapes.Text'>": gs_text3d,
               "<type 'sage.plot.plot3d.shapes.Sphere'>": gs_parametric_plot3d,
               "<type 'sage.plot.plot3d.index_face_set.IndexFaceSet'>": gs_parametric_plot3d,
               "<class 'sage.plot.plot3d.shapes.Box'>": gs_parametric_plot3d,
               "<type 'sage.plot.plot3d.shapes.Cone'>": gs_parametric_plot3d,
               }


    try:
        options[str(type(p))](p)
    except KeyError:
        return "Type not supported"

    json_obj_list = json.dumps(obj_list, separators=(',', ':'))


    # Create div that will contain our 3d scene
    sage_salvus.html("<div id=%s></div>"%id, hide=False)

    # Display the object

    # TODO: do this right. (for dev it's nice to have tmp.js and ._three_data easily accessible.)
    open("tmp.js",'w').write("window._three_data = %s;"%json_obj_list)
    sage_salvus.load("tmp.js")
    sage_salvus.salvus.javascript("$('#%s').threejs({create:window._three_data})"%id)




###
# Interactive 2d Graphics
###

import os, matplotlib.figure

class InteractiveGraphics(object):
    def __init__(self, g, **events):
        self._g = g
        self._events = events

    def figure(self, **kwds):
        if isinstance(self._g, matplotlib.figure.Figure):
            return self._g

        options = dict()
        options.update(self._g.SHOW_OPTIONS)
        options.update(self._g._extra_kwds)
        options.update(kwds)
        options.pop('dpi'); options.pop('transparent'); options.pop('fig_tight')
        fig = self._g.matplotlib(**options)

        from matplotlib.backends.backend_agg import FigureCanvasAgg
        canvas = FigureCanvasAgg(fig)
        fig.set_canvas(canvas)
        fig.tight_layout()  # critical, since sage does this -- if not, coords all wrong
        return fig

    def save(self, filename, **kwds):
        if isinstance(self._g, matplotlib.figure.Figure):
            self._g.savefig(filename)
        else:
            # When fig_tight=True (the default), the margins are very slightly different.
            # I don't know how to properly account for this yet (or even if it is possible),
            # since it only happens at figsize time -- do "a=plot(sin); a.save??".
            # So for interactive graphics, we just set this to false no matter what.
            kwds['fig_tight'] = False
            self._g.save(filename, **kwds)

    def show(self, **kwds):
        fig = self.figure(**kwds)
        ax = fig.axes[0]
        # upper left data coordinates
        xmin, ymax = ax.transData.inverted().transform( fig.transFigure.transform((0,1)) )
        # lower right data coordinates
        xmax, ymin = ax.transData.inverted().transform( fig.transFigure.transform((1,0)) )

        id = '_a' + uuid().replace('-','')

        def to_data_coords(p):
            # 0<=x,y<=1
            return ((xmax-xmin)*p[0] + xmin, (ymax-ymin)*(1-p[1]) + ymin)

        if kwds.get('svg',False):
            filename = '%s.svg'%id
            del kwds['svg']
        else:
            filename = '%s.png'%id

        fig.savefig(filename)

        def f(event, p):
            self._events[event](to_data_coords(p))
        sage_salvus.salvus.namespace[id] = f
        x = {}
        for ev in self._events.keys():
            x[ev] = id

        sage_salvus.salvus.file(filename, show=True, events=x)
        os.unlink(filename)

    def __del__(self):
        for ev in self._events:
            u = self._id+ev
            if u in sage_salvus.salvus.namespace:
                del sage_salvus.salvus.namespace[u]















