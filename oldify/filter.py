from random import randint
from numpy import *
from PIL import Image,ImageDraw


def round_corner(radius, fill):

	corner = Image.new('RGBA',(radius,radius),(0,0,0,0))
	draw = ImageDraw.Draw(corner)
	draw.pieslice((0,0,radius*2,radius*2),180,270,fill=fill)
	return corner

def border(size):

	fill = (255,255,255)
	width, height = size
	radius = int(min(width,height)/8.0)
	offset = int(min(width,height)/15.0)
	rectangle = Image.new('RGB',size,(0,0,0))
	draw = ImageDraw.Draw(rectangle)
	corner = round_corner(radius,fill)
	rectangle.paste(corner,(offset,offset))
	rectangle.paste(corner.rotate(90),(offset,height-radius-offset))
	rectangle.paste(corner.rotate(180),(width-radius-offset,height-radius-offset))
	rectangle.paste(corner.rotate(270),(width-radius-offset,offset))
	draw.rectangle((offset,offset+radius,width-offset,height-offset-radius),fill=fill)
	draw.rectangle((offset+radius,offset,width-offset-radius,height-offset),fill=fill)
	return rectangle

def equalize(l):

	counts = bincount(l.flatten()).astype(float)
	counts/=(1.0*l.size)
	keys = nonzero(counts)[0]
	hist = dict(zip(keys,counts[keys]))
	pdf = {}
	prev = 0

	for value in hist:
		pdf[value] = hist[value] + prev
		prev = pdf[value]

	mapper = lambda i: pdf[i]*255
	mapper = vectorize(mapper)
	L = zeros_like(l)
	for i in range(L.shape[0]):
		L[i] = mapper(l[i])

	return L

def gaussian_kernel(size):
	size = int(size)
	x = mgrid[-size:size+1]
	g = exp(-(x**2/float(size)))
	return g/g.sum()


def blur(im,size=None):
	
	if not size:
		size = (max(im.shape)/15.)
	kernel = gaussian_kernel(size)
	func = lambda row: convolve(row,kernel,'same')
	blurred = apply_along_axis(func,1,im)
	blurred = apply_along_axis(func,1,blurred.T).T
	return blurred
	
def multiply(upper,lower):
	
	return clip((upper*lower)/255.0,0,255)

def screen(upper,lower):

	
	inv_upper = (255 - upper)/255.0
	inv_lower = (255 - lower)/255.0

	screened = 255*(1 - inv_upper * inv_lower)

	return clip(screened,0,255)

def sepia(r,g,b):
	
	r2 = clip(.393*r + .769*g + .189*b,0,255)
	g2 = clip(.349*r + .686*g + .168*b,0,255)
	b2 = clip(.272*r + .534*g + .131*b,0,255)

	return (r2,g2,b2)


def cutout(im,size_x,size_y):
	
	max_y = im.shape[0]
	max_x = im.shape[1]

	x = randint(0,max_x-size_x)
	y = randint(0,max_y-size_y)

	return im[y:y+size_y,x:x+size_x]

def test_filter(filt):

	arr = asarray(Image.open("bros.jpg").convert('L'))
	arr = arr.astype(float)
	filtered = uint8(filt(arr))
	Image.fromarray(filtered).show()


def shinify(im):

	blurred = blur(im)
	return screen(im,blurred)

def make_image(r,g,b):
	r,g,b = map(uint8,(r,g,b))
	return Image.fromarray(dstack((r,g,b)))
    
def show(r,g,b):
    return make_image(r,g,b).show()


def oldify(filename):

	l = asarray(Image.open(filename).convert('L'))

	w = l.shape[1]
	h = l.shape[0]

	brd = border((w,h))
	border_blur_radius = int(max(w,h)/5.0)
	border_px = asarray(brd.convert('L'))
	border_px = blur(border_px,size=border_blur_radius)
	texture = asarray(Image.open("texture.jpg").convert('L'))
	texture = texture.astype(float)
	texture = cutout(texture,w,h)
	texture = (texture - texture.min())/(texture.max()-texture.min())
	texture *= 110
	texture += 145
	
	r,g,b = sepia(l,l,l)
	r,g,b = map(lambda channel: shinify(channel),(r,g,b))
	r,g,b = map(lambda i: multiply(i,texture), (r,g,b))
	r,g,b = map(lambda i: multiply(i,border_px), (r,g,b))
	#show(r,g,b)
	return make_image(r,g,b)
    

