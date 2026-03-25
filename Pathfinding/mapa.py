class Cuadricula:
    def __init__(self, cuadricula):
        self.matriz=cuadricula
        self.ancho=len(cuadricula)
        self.largo=len(cuadricula[0])
        
    def vecinos(self,x:int,y:int):
        for (dx,dy) in [(1,0),(0,1),(-1,0),(0,-1)]:
            result_x=x+dx
            result_y=y+dy
            if 0<=result_x<self.largo and 0<=result_y<self.ancho:
                yield (result_x,result_y)
    
    def dist(self,x:int,y:int):
        return self.matriz[y][x]
    
    #Función necesaria para la implementación de D* Lite y su simulación
    def actualizar_casilla(self,x,y,es_muro,valor=1):
        if es_muro:
            self.matriz[y][x]=float('inf')
        else:
            self.matriz[y][x]=valor
