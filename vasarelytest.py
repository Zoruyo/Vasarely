#import tkinter as tk
import math as math
import svgwrite as svgwrite
import cairosvg as cairosvg
import os
import cv2



def movie(image_folder,video_name,slow_motion=1):    
    images = [img for img in os.listdir(image_folder) if img.endswith(".png")]
    frame = cv2.imread(os.path.join(image_folder, images[0]))
    height, width, layers = frame.shape
    
    video = cv2.VideoWriter(video_name, 0, 40, (width,height))
    
    for image in images:
        for i in range(slow_motion):
            video.write(cv2.imread(os.path.join(image_folder, image)))
    
    cv2.destroyAllWindows()
    video.release()

    
class Point2d:
    def __init__(self,_x=0,_y=0):
        self.x = _x
        self.y = _y
    def __str__(self):
        return "("+str(self.x)+","+str(self.y)+")"
    def norm(self):
        """calcule la norme euclidienne du vecteur"""
        return math.sqrt(self.x**2+self.y**2)
    def dist(self,_A):
        """Calcule la distance euclidienne"""
        return math.sqrt((self.x-_A.x)**2+(self.y-_A.y)**2)

    
class Point3d(Point2d):
    def __init__(self,_anotherPoint=None):
        if _anotherPoint is None: #Si aucune coordonnée n'est définie: (0,0,0,0) par défaut
            super().__init__()
            self.z = 0
            self.beta = 0
        else: #Si un point 2D est défini:
            super().__init__(_anotherPoint.x,_anotherPoint.y) 
            if isinstance(_anotherPoint,Point3d): #isinstance vérifie si _anotherPoint est une instance de point 3D)
                self.z = _anotherPoint.z #On définit ces deux coordonnées en appel une fois les coordonnées x,y définies
                self.beta = _anotherPoint.beta
            else: #Si z et beta ne sont pas définies, elles valent 0 par défaut
                self.z = 0
                self.beta = 0
        
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
        np.x = math.sqrt(self.x**2+self.y**2) #Norme dans R^2
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
        if _profProj != 0:
            self.Cp.z = _profProj
        else:
            self.Cp.z = 1
        self.rayon = _rayon
        self.couleur = _couleur
        
    def __str__(self):     
        return "("+str(self.Cp.x)+","+str(self.Cp.y)+","+str(self.rayon)+","+str(self.Cp.z)+","+str(self.couleur)+")"
    
    '''Rappel:
        a = CA = "distance du point A sur l'axe x par rapport au point C
        c = CC' = "distance du point C' ( pour le cône de projection) sur l'axe z 
        par rapport au point C"
        r = le rayon du cercle dans le plan X x Z
        alpha = l'angle AC'C
    '''
    
    def deformation(self,a,r,c,alpha):
        return a*(1-math.sin(alpha)*(math.cos(math.pi/2-alpha)-math.sqrt((math.cos(math.pi/2-alpha))**2-(1-(r/a)**2))))

    def projPoint(self,_A):
        """calcule les coordonnées du point projeté selon le cone de revolution
           sur la surface de la sphere : A'
        """
        #print("Distance euclidienne entre A et C (projPoint):",_A.dist(self.C))
        #print("Rayon (projPoint):",self.rayon)
        if _A.dist(self.C)>self.rayon: #si la distance est + grande que le cercle, elle est inchangée
            return Point3d(_A) 
        A = Point3d(_A) #On définit le pt en paramètre comme étant un nouveau point 3D (pour des manips)
        A.x -=  self.C.x  #on translate le point _A pour que le centre de la sphere soit en 0,0
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
    
    def biggestradius(self,listeSpheres):
        radius = 0
        for sph in listeSpheres:
            if radius < sph.rayon:
                radius = sph.rayon
        print(radius)        
        return radius   
    
    def lissage(self,L,e,listeSpheres):
        for sph in listeSpheres:
            for i in range(len(L)):
                for j in range(len(L[i])):
                    W = Point3d(L[i][j])
                    if sqrt((W.x-sph.x)**2+(W.y-sph.y)**2) <= R+e and sqrt((W.x-sph.x)**2+(W.y-sph.y)**2) >= R-e:
                        
        '''https://svgwrite.readthedocs.io/en/latest/classes/path.html#svgwrite.path.Path  ''' 
    
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
                #print("Coordonnées grille colonne "+str(i+1)+", ligne "+str(j+1)+ " (indice ("+str(i)+","+str(j)+"):",p)
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
        """fonction qui dessine les carrés contenant les cercles """
        tab_proj = []
        sph_tab = [] #Liste de spoints qui ont bien été projetés sur une sphère
        for i in range(self._nbColonnes):
            tab_proj_col = []
            for j in range(self._nbLignes):
                W = Point3d(self.tab[i][j]) #on définit un point3D à partir du Point2D de la liste tab
                for sph in _listeSphere:
                    w = Point3d(self.tab[i][j])
                    if (w.x,w.y,w.z) not in sph_tab : #Vérifie si le point n'a pas déjà été projeté
                        t = sph.projPoint(self.tab[i][j])
                        #print("test:(",i,",",j,")=",isinstance(t,Point3d))
                        if W is None or t.z > W.z: #Si W est dans la grille, il devient sa projection t, sinon il est égal à (0,0,0,0)
                            if t.x>=0 and t.y>=0 and t.x<self._nbColonnes*self.tailleCase and t.y<self._nbLignes*self.tailleCase: 
                                W = Point3d(t)
                            else:
                                W = None
                            #W.sphere = sph
                    if W is not None and w is not None and W.x != w.x and W.y != w.y and W.z != w.z: #Si le pointa bien été projeté, on l'ajoute à sph_tab
                        sph_tab.append((w.x,w.y,w.z))
                tab_proj_col.append(W)
                #print("Coordonnées grille projection: colonne "+str(i+1)+", ligne "+str(j+1)+ " (indice ("+str(i)+","+str(j)+"):",W)
            tab_proj.append(tab_proj_col)
            
        # on peut lisser
        epsilon = 1/5*self.rayon 
        
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
        #2print(sph_tab)

class Dessin:
    def __init__(self, hauteur = 60, largeur=60):
        #self.grille = Grille(100,100,10)
        #print("Grille=",self.grille)
        #self.sphere1 = Sphere(80,30,120)
        #self.sphere2 = Sphere(-40,-80,100)
        # cas de 2 spheres imbriquées
        # cas de 2 spheres qui se touchent
        #listeSpheres = [Sphere(255,355,122,-150,40),Sphere(305,425,82,-50,40)]#,Sphere(40,80,100,-40,100),Sphere(60,50,140,-40,60)]
        #listeSpheres = [ Sphere(-40,-80,100,-40,100),Sphere(80,30,120,-40,40)]
        #self.dessin = svgwrite.Drawing('test_vasarely.svg', profile='tiny')
        #self.grille.dessineCercles(self.dessin,self.sphere)
        #self.grille.dessineCarres(self.dessin,listeSpheres)
        #self.dessin.save()
        
        if os.getlogin() == "lebre":
            folder = "C:/Users/lebre/.spyder-py3/Projet S4"
            image_folder = folder + "\Products"
            sep = '/'
            src = os.listdir(image_folder)
            for files in src:
                if files.endswith(".svg") or files.endswith(".png") or files.endswith(".avi"):
                    os.remove(image_folder+'/'+files)
        else:
            folder = r"C:\Users\\" + os.getlogin() + r"\Desktop\Projet Vasarely"
            image_folder = folder + r"\Products"
            sep = '\\'
            src = os.listdir(image_folder)
            for files in src:
                if files.endswith(".svg") or files.endswith(".png"):
                    os.remove(image_folder+sep+files)
            src = os.listdir(folder)
            for video in src:
                if video.endswith(".avi"):
                    os.remove(folder+sep+video)

        #
        # animation : 2 spheres se rencontrent
        self.grille = Grille(hauteur,largeur,10)
        start,end = 115,130
        print("Modeling from frame",start,"to",end,"\n\n")
        for i in range(start,end):
            #listeSpheres = [Sphere(-40,-120,40+i),Sphere(-40,-120,120+i)] #sphères imbriquées
            #listeSpheres = [Sphere(120+i,240+i,min(122,20+i),-150*i,40),Sphere(335,465,82,-70+i//20,40)]
            #listeSpheres = [Sphere(120,240,107,-70+2*i//10,40),Sphere(230,300,82,70+i//20,40)]    
            listeSpheres = [Sphere(120+i,240+i,min(122,20+i),-150,40),Sphere(335,465,82,-70+i//20,40)]
            size_numbers = str(max(start,end))
            file_name = image_folder+sep+str(i).zfill(len(size_numbers))+".svg"
            self.dessin = svgwrite.Drawing(file_name, profile='tiny')
            self.grille.dessineCarres(self.dessin,listeSpheres)
            self.dessin.save()
            print(os.path.split(file_name)[1]," saved",end=' ')
            cairosvg.svg2png(url=file_name,write_to=file_name.replace("svg","png"),parent_width=1024,parent_height=660,scale=1.0)
            print("and converted\n")
        video_name = "vasarely.avi"
        movie(image_folder,video_name,10)
        print(video_name," saved\n")


d = Dessin()

'''p3 = Point2d(2,3)
print(p3.norm())'''

'''p1=Point3d(Point2d(2,5)) # Exemple : On définit un point3D comme tel
p1.z = 3
p1.beta = 0

p2 = Point3d(p1) #On peut également définir un point 3D à partir d'un autre point 3D ,comme ceci:
p2.x = 14
p2.y = 7
p2.z = -3
p2.beta = 0.607
print("P2:",p2)'''
'''print("Test distance euclidienne:",p2.dist(p1))'''

'''p3 = p2.rotZ()
print("Rotation de P2:",p3)'''

'''g1 = Grille(5,5,5)'''

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

'''s1 = Sphere(30,10,40,50,50) 
print("Sphère S1:",s1)'''

"""
print("Projection point:",s1.projPoint(p2))
print("Projection distance à partir de P2:",s1.projDist(p2,20))'''
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
