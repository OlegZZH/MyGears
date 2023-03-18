import bpy
from math import *

def createMeshFromData(name, origin, verts, edges):
	# Create mesh and object
	me = bpy.data.meshes.new(name+'Mesh')
	ob = bpy.data.objects.new(name, me)
	ob.location = origin
	ob.show_name = False

	# Link object to scene and make active
	bpy.context.collection.objects.link(ob)
	ob.select_set(True)

	# Create mesh from given verts, faces.
	me.from_pydata(verts, edges, [])
	# Update mesh with new data
	me.update()
	return ob

def TurnPoint( pt, degrees, centerx, centery ):
	fR = sqrt((pt[0] - centerx) * (pt[0] - centerx) + (pt[1] - centery) * (pt[1] - centery))
	fAngle = atan2(pt[1] - centery, pt[0] - centerx)
	fAngle = fAngle + degrees * pi / 180.0

	pt[0] = centerx + fR * cos(fAngle)
	pt[1] = centery + fR * sin(fAngle)

def CreateInvoluteGear( name, points, teeth, centerx, centery ):
	pointlen = len(points)
	edges = [[0, 0] for _ in range(pointlen * teeth) ]
	verts = [[0, 0, 0] for _ in range(pointlen * teeth) ]

	for t in range(teeth):
		for i in range(pointlen):
			verts[t * pointlen + i][0] = points[i][0]
			verts[t * pointlen + i][1] = points[i][1]
			verts[t * pointlen + i][2] = 0
			TurnPoint( verts[t * pointlen + i], t * 360.0 / teeth, 0, 0)
			edges[t * pointlen + i][0] = t * pointlen + i
			edges[t * pointlen + i][1] = t * pointlen + i + 1

	# connect last point with first
	edges[pointlen * teeth - 1][1] = 0

	createMeshFromData( name, [centerx, 0, 0], verts, edges )

points1 = [[8.136,-2.310],[8.152,-2.314],[8.202,-2.323],[8.285,-2.333],[8.403,-2.339],[8.554,-2.338]
,[8.739,-2.325],[8.956,-2.296],[9.203,-2.246],[9.480,-2.173],[9.783,-2.071],[9.902,-1.400]
,[9.651,-1.201],[9.417,-1.037],[9.201,-.906],[9.007,-.804],[8.838,-.729],[8.696,-.676]
,[8.583,-.641],[8.502,-.622],[8.452,-.613],[8.435,-.611],[8.323,-.601],[8.214,-.570]
,[8.113,-.520],[8.023,-.452],[7.947,-.368],[7.888,-.273],[7.847,-.167],[7.826,-.056]
,[7.826,.056],[7.847,.167],[7.888,.273],[7.947,.368],[8.023,.452],[8.113,.520]
,[8.214,.570],[8.323,.601]]

points2 = [[-5.578,.819],[-5.594,.821],[-5.639,.822],[-5.716,.819],[-5.822,.807],[-5.957,.781]
,[-6.119,.738],[-6.306,.673],[-6.516,.583],[-6.747,.463],[-6.993,.310],[-6.993,-.310]
,[-6.747,-.463],[-6.516,-.583],[-6.306,-.673],[-6.119,-.738],[-5.957,-.781],[-5.822,-.807]
,[-5.716,-.819],[-5.639,-.822],[-5.594,-.821],[-5.578,-.819],[-5.460,-.799],[-5.339,-.801]
,[-5.221,-.825],[-5.110,-.870],[-5.008,-.935],[-4.921,-1.017],[-4.849,-1.115],[-4.797,-1.223]
,[-4.766,-1.339],[-4.757,-1.460],[-4.770,-1.579],[-4.805,-1.695],[-4.860,-1.801],[-4.934,-1.896]
,[-5.024,-1.976],[-5.128,-2.038]]

CreateInvoluteGear( "m1_z18_x0", points1, 18, 0, 0 )
CreateInvoluteGear( "m1_z12_x0", points2, 12, 14.9867, 0 )

# OVERLAP DETECTED