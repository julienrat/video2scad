#!/usr/bin/env python2
# -*- coding: utf-8 -*-


#interface de conversion de dessins vers STL
#dependances python-tk, openscad, python2, potrace, pstoedit, imagemagick
# Licence GNU-GPL
# Julien RAT pour les Petits Debrouillards et les amis

import cv2

import Tkinter as tk
from PIL import Image, ImageTk
import subprocess , sys
import argparse



class vid():      
    def __init__(self,cam,root,canvas):
        self.cam = cam
        self.root = root
        self.canvas = canvas

    def update_video(self):
        (self.readsuccessful,self.f) = self.cam.read()
        self.gray_im = cv2.cvtColor(self.f, cv2.COLOR_RGB2GRAY)
        self.im_bw = cv2.threshold(self.gray_im, int(scrollbar.get()), 255, cv2.THRESH_BINARY)[1]
        self.a = Image.fromarray(self.im_bw)
        self.c = self.a.resize((320,240),Image.ANTIALIAS) 
        self.b = ImageTk.PhotoImage(image=self.c)
       
        self.canvas.create_image(0,0,image=self.b,anchor=tk.NW)
        self.root.update()
        self.root.after(33,self.update_video)


class photo():
	def __init__(self,cam,root,canvas):
		self.cam = cam
		self.root = root
		self.canvas = canvas
	def result(self):
		retval, im = cam.read()
		im = cv2.cvtColor(im, cv2.COLOR_RGB2GRAY)
		im_bw = cv2.threshold(im, int(scrollbar.get()), 255, cv2.THRESH_BINARY)[1]
		im_resized = Image.fromarray(im_bw)
		im_resized = im_resized.resize((320,240),Image.ANTIALIAS) 
		cv2.imwrite("pic.png", im_bw)
		subprocess.call("convert pic.png dessin.bmp", shell=True)
		subprocess.call("potrace dessin.bmp -o dessin.eps", shell=True)
		subprocess.call("convert dessin.eps dessin.jpg", shell=True)		
		photo = ImageTk.PhotoImage(im_resized) 
		
		self.canvas.create_image(0,0,image=photo,anchor=tk.NW)
		#root.update()
		root.after(self)

	
	
def take():
	u=photo(cam,root,canvas2)
	root.after(0,u.result)
		
	

	

def Convertir():
	subprocess.call("convert pic.png dessin.bmp", shell=True)
	subprocess.call("potrace dessin.bmp -o dessin.eps", shell=True)
	subprocess.call("convert dessin.eps dessin.jpg", shell=True)
	subprocess.call("pstoedit -dt -f dxf:-polyaslines dessin.eps dessin.dxf", shell=True )	
	f = open('dessin.scad','w')
	
	if int(v.get())==1:
		f.write('linear_extrude(height = '+e.get()+', center = false, convexity = 10)  import (file = "dessin.dxf");')
		print("Extrusion")
		f.close()
		
	if int(v.get())==2:
		f.write('rotate_extrude(convexity = 10) import (file = "dessin.dxf");')
		print("Revolution")
		f.close()
	subprocess.call("openscad -o sortie.stl dessin.scad", shell=True )	

if __name__ == '__main__':	
	root = tk.Tk()
	v = tk.IntVar()
	v.set(2)
	MODES = [("Extrusion", "1"),("Revolution", "2"),]
	parser = argparse.ArgumentParser()
	parser.add_argument("--webcam", help="selectionne une autre webcam")
	args = parser.parse_args()
	if args.webcam:
		cam=cv2.VideoCapture(int(args.webcam))
		print args.webcam
	else:
		cam=cv2.VideoCapture(0)
	videoframe = tk.LabelFrame(root,text='Video')
	videoframe.grid(column=1,row=1,columnspan=1,rowspan=1,padx=5, pady=5, ipadx=5, ipady=5)
	canvas = tk.Canvas(videoframe, width=320,height=240)
	canvas.grid(column=0,row=0,columnspan=4, rowspan=1, padx=5, pady=15)
	canvas2 = tk.Canvas(videoframe, width=320,height=240)
	canvas2.grid(column=0,row=1,columnspan=4, rowspan=1, padx=5, pady=15)
	x = vid(cam,root,canvas)
	root.after(0,x.update_video)
	button = tk.Button(text='Quit',master=videoframe,command=root.destroy)
	button.grid(column=3,row=3)
	bou2 = tk.Button( text='take photo',master=videoframe, command = take)
	bou2.grid(column=1,row=3)
	bou3 = tk.Button( text='convert',master=videoframe, command = Convertir)
	bou3.grid(column=2,row=3)
	for text, mode in MODES:
		swicht = tk.Radiobutton(master=videoframe, text=text, variable=v, value=mode)
		swicht.grid(column=mode,row=4)
	scrollbar = tk.Scale(videoframe, from_=0, to=255,length=100)
	scrollbar.set(127)
	scrollbar.grid(column=4,row=0)
	L1 =tk.Label(videoframe, text="Extrude in mm")
	e = tk.Entry(videoframe,width=4)
	L1.grid(row=2, column=0)
	e.grid(column=1,row=2)
	root.mainloop()
	del cam
