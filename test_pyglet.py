import pyglet
from pyglet.gl import *
from pyglet.window import mouse
import json
import math as m


# Load the GeoJSON data for country coordinates
with open('countries.geojson', 'r') as f:
    geo_data = json.load(f)

# Define the window size
WIDTH, HEIGHT = 800, 600

# Define the initial camera position
camera_pos = [0, 0, -3]

# Define the rotation matrix
rot_x = pyglet.matrix.Matrix().rotate(-45, 1, 0, 0)
rot_y = pyglet.matrix.Matrix().rotate(0, 0, 1, 0)
rot_z = pyglet.matrix.Matrix().rotate(0, 0, 0, 1)

# Define the country highlight color
highlight_color = (1, 0, 0)

# Define the vertex list for the globe surface
globe_verts = []
globe_indices = []
lat_step = 18
lon_step = 36
for i in range(-90 + lat_step, 90 - lat_step, lat_step):
    lat1 = i * math.math.pi / 180
    lat2 = (i + lat_step) * math.pi / 180
    for j in range(0, 360, lon_step):
        lon1 = j * math.pi / 180
        lon2 = (j + lon_step) * math.pi / 180
        globe_verts.append(math.sin(lat1) * math.cos(lon1))
        globe_verts.append(math.sin(lat1) * math.sin(lon1))
        globe_verts.append(math.cos(lat1))
        globe_verts.append(math.sin(lat2) * math.cos(lon1))
        globe_verts.append(math.sin(lat2) * math.sin(lon1))
        globe_verts.append(math.cos(lat2))
        globe_verts.append(math.sin(lat2) * math.cos(lon2))
        globe_verts.append(math.sin(lat2) * math.sin(lon2))
        globe_verts.append(math.cos(lat2))
        globe_verts.append(math.sin(lat1) * math.cos(lon2))
        globe_verts.append(math.sin(lat1) * math.sin(lon2))
        globe_verts.append(math.cos(lat1))
        idx = len(globe_verts) // 3 - 4
        globe_indices.extend([idx, idx + 1, idx + 2, idx + 2, idx + 3, idx])

# Define the vertex list for the country shapes
country_verts = []
for feature in geo_data['features']:
    for coords in feature['geometry']['coordinates']:
        if feature['geometry']['type'] == 'Polygon':
            for point in coords:
                country_verts.extend(point)
        elif feature['geometry']['type'] == 'MultiPolygon':
            for poly in coords:
                for point in poly[0]:
                    country_verts.extend(point)

# Create the window
window = pyglet.window.Window(WIDTH, HEIGHT)

# Set up the OpenGL context
glClearColor(0, 0, 0, 1)
glEnable(GL_DEPTH_TEST)

# Define the OpenGL projection matrix
glMatrixMode(GL_PROJECTION)
glLoadIdentity()
gluPerspective(45, WIDTH / HEIGHT, 0.1, 100.0)

# Define the OpenGL modelview matrix
# gl

@window.event
def on_draw():
    # Clear the window
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    # Set up the OpenGL modelview matrix
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    glTranslatef(camera_pos[0], camera_pos[1], camera_pos[2])
    glMultMatrixf(rot_x.get())
    glMultMatrixf(rot_y.get())
    glMultMatrixf(rot_z.get())

    # Draw the globe
    glColor3f(1, 1, 1)
    glEnableClientState(GL_VERTEX_ARRAY)
    glVertexPointer(3, GL_FLOAT, 0, (GLfloat * len(globe_verts))(*globe_verts))
    glDrawElements(GL_TRIANGLES, len(globe_indices), GL_UNSIGNED_INT, (GLuint * len(globe_indices))(*globe_indices))
    glDisableClientState(GL_VERTEX_ARRAY)

    # Draw the country shapes
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    for feature in geo_data['features']:
        if feature['geometry']['type'] == 'Polygon':
            coords = feature['geometry']['coordinates'][0]
            glColor4f(highlight_color[0], highlight_color[1], highlight_color[2], 0.5)
            glBegin(GL_POLYGON)
            for point in coords:
                glVertex3f(*point_on_globe(point))
            glEnd()
        elif feature['geometry']['type'] == 'MultiPolygon':
            for poly in feature['geometry']['coordinates']:
                coords = poly[0]
                glColor4f(highlight_color[0], highlight_color[1], highlight_color[2], 0.5)
                glBegin(GL_POLYGON)
                for point in coords:
                    glVertex3f(*point_on_globe(point))
                glEnd()
    glDisable(GL_BLEND)

def point_on_globe(point):
    lat, lon = point[1], point[0]
    x = math.sin(lat * math.pi / 180) * math.cos(lon * math.pi / 180)
    y = math.sin(lat * math.pi / 180) * math.sin(lon * math.pi / 180)
    z = math.cos(lat * math.pi / 180)
    return x, y, z

def on_mouse_drag(x, y, dx, dy, buttons, modifiers):
    # Rotate the globe based on the mouse drag
    global rot_x, rot_y
    rot_x = rot_x.rotate(-dy / 5, 1, 0, 0)
    rot_y = rot_y.rotate(-dx / 5, 0, 1, 0)

def on_mouse_scroll(x, y, scroll_x, scroll_y):
    # Zoom the globe based on the mouse scroll
    global camera_pos
    camera_pos[2] += scroll_y * 0.1

def on_mouse_press(x, y, button, modifiers):
    # Highlight the clicked country
    ray = get_ray(x, y)
    closest_point = None
    closest_dist = None
    for feature in geo_data['features']:
        if feature['geometry']['type'] == 'Polygon':
            coords = feature['geometry']['coordinates'][0]
            for i in range(len(coords)):
                a = point_on_globe(coords[i])
                b = point_on_globe(coords[(i+1)%len(coords)])
                point = intersect_line_plane(ray, a, b, (0, 0, 0), (0, 0, 1))
                if point:
                    dist = distance(point, camera_pos)
                    if closest_point is None or dist < closest_dist:
                        closest_point = point
                        closest_dist = dist
                                elif feature['geometry']['type'] == 'MultiPolygon':
            for poly in feature['geometry']['coordinates']:
                coords = poly[0]
                for i in range(len(coords)):
                    a = point_on_globe(coords[i])
                    b = point_on_globe(coords[(i+1)%len(coords)])
                    point = intersect_line_plane(ray, a, b, (0, 0, 0), (0, 0, 1))
                    if point:
                        dist = distance(point, camera_pos)
                        if closest_point is None or dist < closest_dist:
                            closest_point = point
                            closest_dist = dist
    if closest_point:
        highlight_country(closest_point)
    else:
        unhighlight_country()

def get_ray(x, y):
    # Convert screen coordinates to world coordinates
    width, height = window.get_size()
    clip_coord = (2.0 * x / width - 1.0, 1.0 - 2.0 * y / height, -1.0)
    view_matrix = glGetDoublev(GL_MODELVIEW_MATRIX)
    proj_matrix = glGetDoublev(GL_PROJECTION_MATRIX)
    clip_near, clip_far = glGetDoublev(GL_DEPTH_RANGE)
    eye = (-clip_coord[0] * clip_near / proj_matrix[0][0],
           -clip_coord[1] * clip_near / proj_matrix[1][1],
            -clip_near)
    ray = (eye, normalize(math.subtract(mult_matrix_point(view_matrix, eye), (0, 0, 0))))
    return ray

def intersect_line_plane(line, p1, p2, plane_pos, plane_normal):
    # Compute the intersection point of a line and a plane
    denom = dot(line[1], plane_normal)
    if abs(denom) > 0.0001:
        t = dot(math.subtract(plane_pos, line[0]), plane_normal) / denom
        if t >= 0:
            point = add(line[0], scale(line[1], t))
            if point_in_triangle(point, p1, p2, (0, 0, 0)):
                return point

def distance(p1, p2):
    # Compute the distance between two points
    return sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2 + (p1[2]-p2[2])**2)

def normalize(v):
    # Normalize a vector
    mag = sqrt(v[0]**2 + v[1]**2 + v[2]**2)
    return (v[0]/mag, v[1]/mag, v[2]/mag)

def math.subtract(v1, v2):
    # math.subtract two vectors
    return (v1[0]-v2[0], v1[1]-v2[1], v1[2]-v2[2])

def add(v1, v2):
    # Add two vectors
    return (v1[0]+v2[0], v1[1]+v2[1], v1[2]+v2[2])

def dot(v1, v2):
    # Compute the dot product of two vectors
    return v1[0]*v2[0] + v1[1]*v2[1] + v1[2]*v2[2]

def cross(v1, v2):
    # Compute the cross product of two vectors
    return (v1[1]*v2[2]-v1[2]*v2[1], v1[2]*v


