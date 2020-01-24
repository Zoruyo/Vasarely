
#import tkinter as tk
import math as math
import svgwrite as svgwrite
import cairosvg as cairosvg
import os
import cv2



def movie(image_folder,video_name):    
    images = [img for img in os.listdir(image_folder) if img.endswith(".png")]
    frame = cv2.imread(os.path.join(image_folder, images[0]))
    height, width, layers = frame.shape
    
    video = cv2.VideoWriter(video_name, 0, 40, (width,height))
    
    for image in images:
        video.write(cv2.imread(os.path.join(image_folder, image)))
    
    cv2.destroyAllWindows()
    video.release()

    
class Point2d:
    def __init__(self,_x=0,_y=0):
        self.x = _x
        self.y = _y
    def __str__(self):
        return str(self.x)+","+str(self.y)
    def norm(self):
        """calcule la norme euclidienne du vecteur"""
        return math.sqrt(self.x**2+self.y**2)
    def dist(self,_A):
        """Calcule la distance euclidienne"""
        return math.sqrt((self.x-_A.x)**2+(self.y-_A.y)**2)

    
class Point3d(Point2d):
    def __init__(self,_x=0,_y=0,_z=0,_beta=0):
        Point2d.__init__(self,_x,_y)
        self.z = _z
        self.beta = _beta
        
    def __str__(self):
        return "("+str(self.x)+","+str(self.y)+","+str(self.z)+","+str(self.beta)+")"

    def norm(self):
        """calcule la norme du vecteur"""
        return math.sqrt(self.x**2+self.y**2+self.z**2)

    def rotZ(self):
        """rotation autour de l'axe z : retourne un nouveau point qui correspond
        à la projection du point sur l'axe x (beta contient l'angle)
        """
        np = Point3d()
        np.x = math.sqrt(self.x**2+self.y**2)
        np.y = 0
        np.z = 0
        if np.x!=0:
            np.beta = math.acos(self.x/np.x)
        if self.y<0:
            np.beta = -np.beta
        return np

    def arcRotZ(self,_beta = None):
        """rotation inverse autour de l'axe z"""
        t = self.x
        if _beta!=None:
            self.beta = _beta
        self.x = t*math.cos(self.beta)
        self.y = t*math.sin(self.beta)
        # on ne change pas z
        # self.z = 0;

    def dist(self,_A):
        """Calcule la distance euclidienne"""
        return math.sqrt((self.x-_A.x)**2+(self.y-_A.y)**2+(self.z-_A.z)**2)

    
class Sphere:
    def __init__(self,_x = 0,_y=0, _rayon = 50, _profProj = -40, _couleur = 10):
        self.C = Point3d()
        self.C.x = _x
        self.C.y = _y
        self.C.z = 0
        self.Cp = Point3d(self.C)
        self.Cp.z = _profProj
        self.rayon = _rayon
        self.couleur = _couleur

    def deformation(self,a,r,c,alpha):
        return a*(1-math.sin(alpha)*(math.cos(math.pi/2-alpha)-math.sqrt((math.cos(math.pi/2-alpha))**2-(1-(r/a)**2))))

    def projPoint(self,_A):
        """calcule les coordonnées du point projeté selon le cone de revolution
           sur la surface de la sphere : A'
        """
        if _A.dist(self.C)>self.rayon:
            return Point3d(_A)
        #on translate le point _A pour que le centre de la sphere soit en 0,0
        A = Point3d(_A)
        A.x -=  self.C.x
        A.y -=  self.C.y
        A = A.rotZ()
        a = A.x
        r = self.rayon
        c = self.C.dist(self.Cp)
        alpha = math.atan(a/c)
        X = Point3d();
        if a!= 0:
            X.x = self.deformation(a,r,c,alpha)
            X.z = math.sqrt(r**2-X.x**2)
        else:
            X.x = 0
            X.z = r
        X.y = 0
        X.arcRotZ(A.beta)
        #on retranslate le point obtenu pour le remettre à la bonne place
        X.x += self.C.x
        X.y += self.C.y
        return X

    def projDist(self,_A,_d):
        """calcule la projection d'une distance à partir d'un point"""
        if _A.dist(self.C)>self.rayon:
            return _d
        #on calcule la projection du 1er point
        # A REVOIR car la translationà l'origine n'a pas été faite.
        A = _A.rotZ()
        a = A.x
        r = self.rayon
        c = self.C.dist(self.Cp)
        alpha = math.atan(a/c)
        X = Point3d();
        if a!= 0:
            X.x = self.deformation(a,r,c,alpha)
        else:
            X.x = 0
        X.y = 0
        X.z = 0
        #deuxieme point
        a = A.x+_d
        alpha = math.atan(a/c)
        Y = Point3d();
        if a!= 0:
            Y.x = self.deformation(a,r,c,alpha)
        else:
            Y.x = 0
        Y.y = 0
        Y.z = 0
        #on retourne la distance entre les 2 points X et Y
        return X.dist(Y)

    
class Grille:
    def __init__(self,_nbColonnes, _nbLignes, _tailleCase):
        self.tailleCase = _tailleCase
        self._nbColonnes = _nbColonnes
        self._nbLignes = _nbLignes
        #le tableau des coordonnées
        self.tab = []
        for i in range(_nbColonnes):
            col = []
            for j in range(_nbLignes):
                p = Point2d(i*_tailleCase,j*_tailleCase)
                col.append(p)
            self.tab.append(col)

    def __str__(self):
        return str(self.tab)

    """    def dessineCercles(self,_svgDraw,_sphere):
        for col in self.tab:
            for case in col:
                print(case)
                A0 = Point3d()
                A0.x = case[0]
                A0.y = case[1]
                A0.z = 0
                print(A0)
                X = _sphere.projPoint(A0)
                print(X)
                rayon = _sphere.projDist(A0,self.tailleCase//2)
                #on decale pour ne pas avoir de coordonnées negatives
                xt = (self._largeur//2+2)*self.tailleCase+X.x
                yt = (self._hauteur//2+2)*self.tailleCase+X.y
                _svgDraw.add(_svgDraw.ellipse(center=(xt, yt), r=(rayon, rayon),fill="none", stroke="red")) """

    def dessineCarres(self,_svgDraw,_listeSphere):
        """fonction qui dessinne les carrés contenant les cercle """
        tab_proj = []
        for i in range(self._nbColonnes):
            tab_proj_col = []
            for j in range(self._nbLignes):
                W = Point3d(self.tab[i][j])
                for sph in _listeSphere:
                    t = sph.projPoint(self.tab[i][j])
                    #print("test:(",i,",",j,")=",isinstance(t,Point3d))
                    if W is None or t.z > W.z:
                        if t.x>=0 and t.y>=0 and t.x<self._nbColonnes*self.tailleCase and t.y<self._nbLignes*self.tailleCase:
                            W = Point3d(t)
                        else:
                            W = None
                        #W.sphere = sph
                tab_proj_col.append(W)
            tab_proj.append(tab_proj_col)
        #
        # #on peut dessiner
        for i in range(self._nbColonnes-1):
            for j in range(self._nbLignes-1):
                P = tab_proj[i][j]
                Q = tab_proj[i][j+1]
                R = tab_proj[i+1][j]
                if not P is None and not Q is None:
                    _svgDraw.add(_svgDraw.line((P.x, P.y), (Q.x, Q.y), stroke=svgwrite.rgb(10, 10, 100, '%')))
                if not P is None and not R is None:
                    _svgDraw.add(_svgDraw.line((P.x, P.y), (R.x, R.y), stroke=svgwrite.rgb(10, 100, 16, '%')))


class Dessin:
    def __init__(self, hauteur = 100, largeur=100):
        self.grille = Grille(100,100,10)
        print("Grille=",self.grille)
        #self.sphere1 = Sphere(80,30,120)
        #self.sphere2 = Sphere(-40,-80,100)
        # cas de 2 spheres imbriquées
        #listeSpheres = [ Sphere(-40,-120,40),Sphere(-40,-120,120)]
        # cas de 2 spheres qui se touchent
        listeSpheres = [Sphere(255,355,122,-150,40),Sphere(305,425,82,-50,40)]#,Sphere(40,80,100,-40,100),Sphere(60,50,140,-40,60)]
        #listeSpheres = [ Sphere(-40,-80,100,-40,100),Sphere(80,30,120,-40,40)]
        self.dessin = svgwrite.Drawing('test_vasarely.svg', profile='tiny')
        #self.grille.dessineCercles(self.dessin,self.sphere)
        self.grille.dessineCarres(self.dessin,listeSpheres)
        self.dessin.save()
        
        image_folder = "C:/Users/lebre/.spyder-py3/Projet S4"
        src = os.listdir(image_folder)
        for files in src:
            if files.endswith(".svg") or files.endswith(".png") or files.endswith(".avi"):
                os.remove(image_folder+'/'+files)

        #
        # animation : 2 spheres se rencontrent
        self.grille = Grille(60,60,10)
        for i in range(400):
            listeSpheres = [Sphere(120+i,240+i,min(122,20+i),-150,40),Sphere(335,465,82,-70+i//20,40)]
            file_name = str(i).zfill(5)+".svg"
            self.dessin = svgwrite.Drawing(file_name, profile='tiny')
            self.grille.dessineCarres(self.dessin,listeSpheres)
            self.dessin.save()
            print(file_name," saved\n")
            cairosvg.svg2png(url=str(i).zfill(5)+".svg",write_to=str(i).zfill(5)+".png",parent_width=1024,parent_height=660,scale=1.0)
            print(file_name," converted\n")
        video_name = "vasarely.avi" 
        movie(image_folder,video_name)



d = Dessin()

'''p1=Point3d()
print(p1)'''

""" tests pour vérifier que la projection fonctionne
S1 = Sphere(-40,-120,40)
S2 = Sphere(-40,-120,120)
A = Point()
A.x = -40
A.y = -120
A.z = 0
print("A=",A)
t = S1.projPoint(A)
print("A=",A)
print("t=",t)
z = S2.projPoint(A)
print("A=",A)
print("z=",z)
"""


"""
dwg = svgwrite.Drawing('test.svg', profile='tiny')
dwg.add(dwg.line((0, 0), (10, 0), stroke=svgwrite.rgb(10, 10, 16, '%')))
dwg.add(dwg.text('Test', insert=(0, 0.2)))
dwg.add(dwg.ellipse(center=(10, 20), r=(5, 10),fill="none", stroke="blue"))
dwg.add(dwg.ellipse(center=(100, 50), r=(80, 40),fill="none", stroke="red"))
dwg.add(dwg.ellipse(center=(200, 250), r=(80, 80),fill="none", stroke="red"))
dwg.save()
"""

"""
A0=Point()
A0.x = 2
A0.y = -3
A0.z = 0
A=A0.rotZ()
print(A0)
print(A)
print("beta=",A.beta)
A.arcRotZ()
print(A)
S = Sphere()
X = S.proj(A0)
print(X)
"""

'''if _anotherPoint is None:
    super().__init__()
    self.z = 0
    self.beta = 0
else:
    super().__init__(_anotherPoint.x,_anotherPoint.y)
    if isinstance(_anotherPoint,Point3d): #isinstance vérifie si _anotherPoint est une instance de point 3D)
        self.z = _anotherPoint.z
        self.beta = _anotherPoint.beta
    else:
        self.z = 0
        self.beta = 0'''
