import pygame
from OpenGL.GL import *
from OpenGL.GLU import *
from PIL import Image
from math import *
import json
import urllib.request

pygame.init()
window = pygame.display.set_mode((800, 600), pygame.OPENGL | pygame.DOUBLEBUF)
glMatrixMode(GL_PROJECTION)
glLoadIdentity()
gluPerspective(45, 800/600, 0.1, 100.0)
glMatrixMode(GL_MODELVIEW)
glLoadIdentity()
glTranslatef(0, 0, -5)

with urllib.request.urlopen("https://raw.githubusercontent.com/johan/world.geo.json/master/countries.geo.json") as url:
    data = json.loads(url.read().decode())
    
def load_texture(filename):
    # Load an image file and convert it to a texture
    image = Image.open(filename)
    image = image.transpose(Image.FLIP_TOP_BOTTOM)
    width, height = image.size
    image_data = image.convert("RGBA").tobytes()
    texture = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, image_data)
    return texture

def draw_sphere(radius, texture):
    # Draw a sphere with a given radius and texture
    glPushMatrix()
    glTranslatef(0, 0, -radius)
    glRotatef(-90, 1, 0, 0)
    slices, stacks = 40, 40
    phi = pi / stacks
    theta = 2 * pi / slices
    for i in range(stacks):
        glBegin(GL_QUAD_STRIP)
        for j in range(slices+1):
            x = cos(j*theta) * sin(i*phi)
            y = sin(j*theta) * sin(i*phi)
            z = cos(i*phi)
            glNormal3f(x, y, z)
            glTexCoord2f(j/slices, i/stacks)
            glVertex3f(radius*x, radius*y, radius*z)
            x = cos(j*theta) * sin((i+1)*phi)
            y = sin(j*theta) * sin((i+1)*phi)
            z = cos((i+1)*phi)
            glNormal3f(x, y, z)
            glTexCoord2f(j/slices, (i+1)/stacks)
            glVertex3f(radius*x, radius*y, radius*z)
        glEnd()
    glPopMatrix()

def point_on_globe(coord):
    # Convert a geographic coordinate to a point on the globe
    lat, lon = coord
    x = cos(radians(lat)) * cos(radians(lon))
    y = cos(radians(lat)) * sin(radians(lon))
    z = sin(radians(lat))
    return (x, y, z)

def point_in_triangle(point, v1, v2, v3):
    # Check if a point is inside a triangle
    v1 = subtract(v1, v1)
    v2 = subtract(v2, v1)
    v3 = subtract(v3, v1)
    point = subtract(point, v1)
    dot00 = dot_product(v2, v2)
    dot01 = dot_product(v2, v3)
    dot02 = dot_product(v2, point)
    dot11 = dot_product(v3, v3)
    dot12 = dot_product(v3, point)
    inv_denom = 1 / (dot00 * dot11 - dot01 * dot01)
    u = (dot11 * dot02 - dot01 * dot12) * inv_denom
    v = (dot00 * dot12 - dot01 * dot02) * inv_denom
    return u >= 0 and v >= 0 and u + v < 1

def get_clicked_country(coord):
    # Get the country that was clicked on
    for feature in data['features']:
        if feature['geometry']['type'] == 'Polygon':
            for i, ring in enumerate(feature['geometry']['coordinates']):
                if any(point_in_triangle(point_on_globe(coord), point_on_globe(ring[j]), point_on_globe(ring[j+1]), point_on_globe(ring[(j+2)%len(ring)])) for j in range(len(ring))):
                    return feature
        elif feature['geometry']['type'] == 'MultiPolygon':
            for poly in feature['geometry']['coordinates']:
                for i, ring in enumerate(poly):
                    if any(point_in_triangle(point_on_globe(coord), point_on_globe(ring[j]), point_on_globe(ring[j+1]), point_on_globe(ring[(j+2)%len(ring)])) for j in range(len(ring))):
                        return feature
    return None

texture = load_texture("worldmap.jpg")
highlight_texture = load_texture("highlight.png")
highlight_country = None

clock = pygame.time.Clock()
while True:
    clock.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 4:
                glTranslatef(0, 0, 0.1)
            elif event.button == 5:
                glTranslatef(0, 0, -0.1)
            elif event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                mouse_coord = ((mouse_pos[1] - 300) / 300 * 90, (mouse_pos[0] - 400) / 400 * 180)
                highlight_country = get_clicked_country(mouse_coord)
                print(highlight_country['properties']['name'] if highlight_country else "No country")
        elif event.type == pygame.MOUSEMOTION and event.buttons[0]:
            glRotatef(event.rel[1], 1, 0, 0)
            glRotatef(event.rel[0], 0, 1, 0)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_TEXTURE_2D)
    draw_sphere(1.0, texture)
    if highlight_country:
        glColor4f(1, 1, 1, 0.5)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        draw_sphere(1.0, highlight_texture)
        glDisable(GL_BLEND)
    pygame.display.flip()

