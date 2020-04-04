import math as math
import svgwrite as svgwrite
import cairosvg as cairosvg
import os
import random
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

def ordreSphere(listeSpheres):
    listeSpheres = list(listeSpheres)
    listeSpheres2 = []
    listeRayon = []
    while listeSpheres != []:
        radius = 0
        for sph in listeSpheres:
            if radius < sph.rayon:
                radius = sph.rayon
        for sph in listeSpheres:
            if sph.rayon == radius:
                listeSpheres2.append(sph)
                listeRayon.append(sph.rayon)
                listeSpheres.remove(sph)
                break
    #print(listeRayon)
    return listeSpheres2

def biggestradius(listeSpheres):
    radius = 0
    for sph in listeSpheres:
        if radius < sph.rayon:
            radius = sph.rayon     
    return radius  

def randomcolor():
    colors = ["red","green","blue"]
    color = random.choice(colors)
    return color   

def permutTab(tab_proj_col, W):
    tab_proj_col2 = []
    while len(tab_proj_col) > 1 and str(tab_proj_col[0]) != str(W):
        #Tableau [<__main__.Point3d object at 0x0000015144574880>]
        #Point   ['<__main__.Point3d object at 0x0000015144516D30>']
        for X in tab_proj_col:
            if X != W:
                tab_proj_col2.append(X)
                tab_proj_col.remove(X)
                break
    return(tab_proj_col2)
    
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
        #Si aucune coordonnée n'est définie: (0,0,0,0) par défaut
        if _anotherPoint is None:
            super().__init__()
            self.z = 0
            self.beta = 0
        #Si un point 2D est défini:
        else:
            super().__init__(_anotherPoint.x,_anotherPoint.y) 
            #isinstance vérifie si _anotherPoint est une instance de Point3d
            if isinstance(_anotherPoint,Point3d):
                self.z = _anotherPoint.z
                self.beta = _anotherPoint.beta
            #Si z et beta ne sont pas définies, elles valent 0 par défaut
            else:
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
        np.x = super().norm()
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
    def dist(self,_A):
        """Calcule la distance euclidienne"""
        return math.sqrt((self.x-_A.x)**2+(self.y-_A.y)**2+(self.z-_A.z)**2)
    def inSpheres(self,_listeSphere):
        biais = 10**(-2)
        #biais = 0
        listeSphere = []
        for sph in _listeSphere:
            if self.dist(sph.C) <= sph.rayon+biais:
                listeSphere.append(sph)
        return listeSphere

    
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

    def projPoint(self,_A,e):
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
        a = A.x + e
        r = self.rayon
        c = self.C.dist(self.Cp)
        alpha = math.atan(a/c)
        X = Point3d()
        if a >= r: #Erreur de projection au delà du rayon: on retire epsilon à a
            X.x = self.deformation(a-e,r,c,alpha)
            X.z = math.sqrt(r**2-(X.x)**2)
        elif (a < r and a != e): #On "pousse" les points du centre de la sphère en ajoutant epsilon, ce qui crée l'effet loupe, on les décale d'une longueur de "epsilon"
            X.x = self.deformation(a-e,r,c,alpha) 
            X.z = math.sqrt(r**2-X.x**2)  
        if a == e: #Correspond au sommet de la sphère
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
        X = Point3d()
        if a!= 0:
            X.x = self.deformation(a,r,c,alpha)
        else:
            X.x = 0
        X.y = 0
        X.z = 0
        #deuxieme point
        a = A.x+_d
        alpha = math.atan(a/c)
        Y = Point3d()
        if a!= 0:           
            Y.x = self.deformation(a,r,c,alpha)
        else:
            Y.x = 0
        Y.y = 0
        Y.z = 0
        #on retourne la distance entre les 2 points X et Y
        return X.dist(Y)             
                    
                        
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

    def dessineCarres(self,_listeSphere):
        """fonction qui dessine les carrés contenant les cercles """
        e = 15
        tab_proj = []
        for i in range(self._nbColonnes):
            tab_proj_col = []
            for j in range(self._nbLignes):
                w = self.tab[i][j]
                W = Point3d(w) #on définit un point3D à partir du Point2D de la liste tab
                for sph in _listeSphere:
                    t = sph.projPoint(w,e)
                    t_listeSphere = t.inSpheres(_listeSphere) #on cherche les sphères qui contiennent t
                    if len(t_listeSphere) >= 1:
                        biggestSphere = ordreSphere(t_listeSphere)[0]
                        if sph == biggestSphere: #on vérifie qu'on projette t sur la plus grande sphère
                            if W is None or t.z > W.z: #Si W est dans la grille, il devient sa projection t, sinon il est égal à (0,0,0,0)
                                if t.x>=0 and t.y>=0 and t.x<self._nbColonnes*self.tailleCase and t.y<self._nbLignes*self.tailleCase:
                                    W = Point3d(t)
                                else:
                                    W = None
                        else:
                            W_t_listeSphere = W.inSpheres(t_listeSphere)
                            if W_t_listeSphere != t_listeSphere: #si le point projeté est dans un ensemble différent de sphère
                                Wp = biggestSphere.projPoint(t,e)
                                if Wp.inSpheres(t_listeSphere) == t_listeSphere: #on projette à nouveau le point pour qu'il colle à la plus grande
                                    if W is None or Wp.z > W.z: #Si W est dans la grille, il devient sa projection t, sinon il est égal à (0,0,0,0)
                                        if Wp.x>=0 and Wp.y>=0 and Wp.x<self._nbColonnes*self.tailleCase and Wp.y<self._nbLignes*self.tailleCase:
                                            W = Point3d(Wp)
                                        else:
                                            W = None
                tab_proj_col.append(W)
            tab_proj.append(tab_proj_col)
        return tab_proj
 
      
    #on peut dessiner
    def dessiner(self,tab_proj,_svgDraw,listeSpheres):
        e = 20
        listeP = []
        listeQ = [] #On conserve également les points Q et R pour pouvoir appliquer Bézier par la suite sur chaque couple (P,Q) de l'intervalle [R+e,R-e]
        listeR = []
        for i in range(self._nbColonnes-1):
            for j in range(self._nbLignes-1):
               color1 = randomcolor()
               color2 = randomcolor()
               while color2 == color1:
                  color2 = randomcolor()
               P = tab_proj[i][j]
               Q = tab_proj[i][j+1]
               R = tab_proj[i+1][j]
               S = tab_proj[i+1][j+1]
               c = P.dist(Q)
               C = Point3d()
               C.x = (Q.x+R.x)/2
               C.y = (Q.y+R.y)/2
               C.z = (Q.z+R.z)/2                   
               for sph in listeSpheres:
                   P0 = Point3d(P)
                   P0.z = 0
                   if P0.dist(sph.C) <= sph.rayon + e and P0.dist(sph.C) >= sph.rayon - e:
                       listeP.append(P)
                       listeQ.append(Q)
                       listeR.append(R)
               if not P is None and not Q is None and P not in listeP:
                    """ 3 façons de tracer une ligne:
                    1. fonction ligne
                    2. fonction path avec commande ligne
                    3. fonction path avec commande quadratique bézier (moins optimisée mais adaptable pour lissage) """
                    # 1.
                    #_svgDraw.add(_svgDraw.line((P.x, P.y), (Q.x, Q.y), stroke=svgwrite.rgb(10, 100, 100, '%')))
                    # 2. M: indique le début de tracé; P = Point de départ; l: indique la méthode "ligne"; (Q.x-P.x,Q.y-P.y) = vecteur à appliquer à P
                    #line_path = "M "+str(P.x)+' '+str(P.y)+" l "+str(Q.x-P.x)+' '+str(Q.y-P.y)
                    #_svgDraw.add(_svgDraw.path(line_path, stroke=svgwrite.rgb(10, 10, 100, '%')))
                    # 3. M: indique le début de tracé; P = Point de départ; q: indique la méthode "quadratique"; (Q.x-S.x,Q.y-S.y) = (O,O) vecteur nul "ressort" qui tire la courbe; (Q.x-P.x,Q.y-P.y) = vecteur à appliquer à P
                    quad_path = "M "+str(P.x)+' '+str(P.y)+" q "+str(0)+' '+str(0)+' '+str(Q.x-P.x)+' '+str(Q.y-P.y)
                    _svgDraw.add(_svgDraw.path(quad_path, stroke=svgwrite.rgb(10, 10, 100, '%')))
               elif P in listeP:   
                    quad_path = "M "+str(P.x)+' '+str(P.y)+" q "+str(10)+' '+str(10)+' '+str(Q.x-P.x)+' '+str(Q.y-P.y)
                    _svgDraw.add(_svgDraw.path(quad_path, fill="none", stroke=svgwrite.rgb(100, 10, 10, '%'))) #On applique une courbure de Bézier (à définir pour chaque couple (P,Q))
               if not P is None and not R is None and P not in listeP:
                    #_svgDraw.add(_svgDraw.line((P.x, P.y), (R.x, R.y), stroke=svgwrite.rgb(10, 100, 16, '%')))
                    quad_path = "M "+str(P.x)+' '+str(P.y)+" q "+str(0)+' '+str(0)+' '+str(R.x-P.x)+' '+str(R.y-P.y)
                    _svgDraw.add(_svgDraw.path(quad_path, stroke=svgwrite.rgb(10, 100, 16, '%')))
               elif P in listeP:
                    quad_path = "M "+str(P.x)+' '+str(P.y)+" q "+str(10)+' '+str(10)+' '+str(R.x-P.x)+' '+str(R.y-P.y)
                    _svgDraw.add(_svgDraw.path(quad_path, fill="none", stroke=svgwrite.rgb(100, 10, 10, '%'))) #on applique une courbure de Bézier (à définir pour chaque couple (P,R))
               if C.z == 0:    
                    _svgDraw.add(_svgDraw.circle(center=(C.x,C.y),r=c/2, fill=color1, stroke=svgwrite.rgb(10, 100, 16, '%'),stroke_width=1/2)) 
                    _svgDraw.add(_svgDraw.circle(center=(C.x,C.y),r=c/3, fill=color2, stroke=svgwrite.rgb(10, 100, 16, '%'),stroke_width=1/2))   
               else:
                   '''P.z -= P.z
                   Q.z -= Q.z #Contre-exemples pour le théorème de Pitot
                   R.z -= R.z
                   S.z -= S.z
                   print([P.dist(Q)+R.dist(S),P.dist(R)+Q.dist(S)])'''
        # Affichage des intervalles [R-e,R+e] de la liste de sphères n°4 à la frame n°115
        for sph in listeSpheres:
            _svgDraw.add(_svgDraw.circle((sph.C.x,sph.C.y), sph.rayon-e, fill="none", stroke=svgwrite.rgb(100, 10, 10, '%')))
            _svgDraw.add(_svgDraw.circle((sph.C.x,sph.C.y), sph.rayon+e, fill="none", stroke=svgwrite.rgb(100, 10, 10, '%'))) 
      

    """J'AI MIS EN COMMENTAIRE LA FONCTION ACTUELLE ET MIS LA FONCTION DESSINER D'AVANT DISJONCTION
    DES CAS POUR VISUALISER COMMENT CA SE PASSE NIVEAU COLLISION"""

    '''
    #on peut dessiner
    def dessiner(self,tab_proj,_svgDraw,listeSpheres):
        for i in range(self._nbColonnes-1):
            for j in range(self._nbLignes-1):
                color1 = randomcolor()
                color2 = randomcolor()
                while color2 == color1:
                    color2 = randomcolor()
                P = tab_proj[i][j]
                Q = tab_proj[i][j+1]
                R = tab_proj[i+1][j]
                c = P.dist(Q)
                C = Point3d()
                C.x = (Q.x+R.x)/2
                C.y = (Q.y+R.y)/2
                C.z = (Q.z+R.z)/2    
                if not P is None and not Q is None:
                    """ 3 façons de tracer une ligne:
                    1. fonction ligne
                    2. fonction path avec commande ligne
                    3. fonction path avec commande quadratique bézier (moins optimisée mais adaptable pour lissage) """
                    # 1.
                    #_svgDraw.add(_svgDraw.line((P.x, P.y), (Q.x, Q.y), stroke=svgwrite.rgb(10, 100, 100, '%')))
                    # 2. M: indique le début de tracé; P = Point de départ; l: indique la méthode "ligne"; (Q.x-P.x,Q.y-P.y) = vecteur à appliquer à P
                    #line_path = "M "+str(P.x)+' '+str(P.y)+" l "+str(Q.x-P.x)+' '+str(Q.y-P.y)
                    #_svgDraw.add(_svgDraw.path(line_path, stroke=svgwrite.rgb(10, 10, 100, '%')))
                    # 3. M: indique le début de tracé; P = Point de départ; q: indique la méthode "quadratique"; (Q.x-S.x,Q.y-S.y) = (O,O) vecteur nul "ressort" qui tire la courbe; (Q.x-P.x,Q.y-P.y) = vecteur à appliquer à P
                    quad_path = "M "+str(P.x)+' '+str(P.y)+" q "+str(0)+' '+str(0)+' '+str(Q.x-P.x)+' '+str(Q.y-P.y)
                    _svgDraw.add(_svgDraw.path(quad_path, stroke=svgwrite.rgb(10, 10, 100, '%')))
                if not P is None and not R is None:
                    _svgDraw.add(_svgDraw.line((P.x, P.y), (R.x, R.y), stroke=svgwrite.rgb(10, 100, 16, '%'))


        # Affichage des intervalles [R-e,R+e] de la liste de sphères n°4 à la frame n°115
        for sph in listeSpheres:
            _svgDraw.add(_svgDraw.circle((sph.C.x,sph.C.y), sph.rayon-e, fill="none", stroke=svgwrite.rgb(100, 10, 10, '%')))
            _svgDraw.add(_svgDraw.circle((sph.C.x,sph.C.y), sph.rayon+e, fill="none", stroke=svgwrite.rgb(100, 10, 10, '%'))) 
'''

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
            image_folder = folder
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
            src = os.listdir(image_folder)
            for video in src:
                if video.endswith(".avi"):
                    os.remove(image_folder+sep+video)
        
        # animation : 2 spheres se rencontrent
        self.grille = Grille(hauteur,largeur,10)
        start,end = 85,85
        print("Modeling from frame",start,"to",end,"\n\n")
        for i in range(start,end+1):
            print(round(((i-start)/(end-start+1)*100),1),'%')
            #listeSpheres = [Sphere(-40,-120,40+i),Sphere(-40,-120,120+i)] #sphères imbriquées
            #listeSpheres = [Sphere(120+i,240+i,min(122,20+i),-150*i,40),Sphere(335,465,82,-70+i//20,40)]
            #listeSpheres = [Sphere(120,240,107,-70+2*i//10,40),Sphere(230,300,82,70+i//20,40)]    
            listeSpheres = [Sphere(120+i,240+i,min(122,20+i),-150,40),Sphere(335,465,82,-70+i//20,40)]
            size_numbers = str(max(start,end))
            file_name = image_folder+sep+str(i).zfill(len(size_numbers))+".svg"
            self.dessin = svgwrite.Drawing(file_name, profile='tiny')
            tab_proj = self.grille.dessineCarres(listeSpheres)
            #tab_proj = self.grille.lissage(tab_proj,listeSpheres)
            self.grille.dessiner(tab_proj,self.dessin,listeSpheres)
            self.dessin.save()
            print('\t',os.path.split(file_name)[1]," saved")
            cairosvg.svg2png(url=file_name,write_to=file_name.replace("svg","png"),parent_width=1024,parent_height=660,scale=1.0)
            print('\t',"and converted\n")
        print("100 %\n")
        video_name = image_folder+sep+"vasarely.avi"
        slow_motion = 5
        movie(image_folder,video_name,slow_motion)
        print('\t',os.path.split(video_name)[1],"saved\n")


d = Dessin()

'''
p3 = Point2d(2,3)
print(p3.norm())

p1=Point3d(Point2d(2,5)) # Exemple : On définit un point3D comme tel
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
print("Sphère S1:",s1)
print(s1.rayon)'''

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
