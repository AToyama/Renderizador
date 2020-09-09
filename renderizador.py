# Desenvolvido por: Luciano Soares <lpsoares@insper.edu.br>
# Disciplina: Computação Gráfica
# Data: 28 de Agosto de 2020

import argparse     # Para tratar os parâmetros da linha de comando
import x3d          # Faz a leitura do arquivo X3D, gera o grafo de cena e faz traversal
import interface    # Janela de visualização baseada no Matplotlib
import gpu          # Simula os recursos de uma GPU

def convert_rgb(color):
  return [round(255*n) for n in color]

def line(x, y, x0, y0, x1, y1):
    """
    x,y - ponto sendo checado se esta dentro ou fora da linha
    x0, y0, x1 ,y0 - coordenadas dos dois vertices da linha
    """

    dx = x1 - x0
    dy = y1 - y0
        
    if ((x - x0)*dy - (y - y0)*dx) > 0:
        return True
    else:
        return False

def inside(x, y, vertices):

    x0 = vertices[0]
    y0 = vertices[1]
    x1 = vertices[2]
    y1 = vertices[3]
    x2 = vertices[4]
    y2 = vertices[5]

    line1 = line(x ,y, x0, y0, x1, y1)
    line2 = line(x ,y, x1, y1, x2, y2)
    line3 = line(x ,y, x2, y2, x0, y0)

    return line1 and line2 and line3

def polypoint2D(point, color):
    """ Função usada para renderizar Polypoint2D. """

    rgb_color = convert_rgb(color)

    for i in range(0, len(point), 2):
        gpu.GPU.set_pixel(int(point[i]), int(point[i+1]), rgb_color[0], rgb_color[1], rgb_color[2])

def polyline2D(lineSegments, color):
    """ Função usada para renderizar Polyline2D. """
    
    rgb_color = convert_rgb(color)
    
    # vertices da linha
    x0 = lineSegments[0]
    y0 = lineSegments[1]
    x1 = lineSegments[2]
    y1 = lineSegments[3]

    # calcula a diferença entre os vertices nos eixos x e y
    dx = x1 - x0
    dy = y1 - y0

    #  calcula o numero de pixels necessarios pra fazer a linha
    n_pixels = round(abs(dx) if abs(dx) > abs(dy) else abs(dy))

    # calcula o quanto é necessário incrementar em x e y para cada novo pixel
    Xinc = dx / n_pixels
    Yinc = dy / n_pixels

    # calcula os valores de x e y para cada pixel e adiciona na lista
    X = x0
    Y = y0
    pixels = []
    for i in range(int(n_pixels)+1):
        pixels.append((X,Y))
        X += Xinc
        Y += Yinc

    for x,y in pixels:
        gpu.GPU.set_pixel(int(x), int(y), rgb_color[0], rgb_color[1], rgb_color[2])

def triangleSet2D(vertices, color):
    """ Função usada para renderizar TriangleSet2D. """

    rgb_color = convert_rgb(color)

    # itera por todos os pixels do grid
    for x in range(LARGURA):
        for y in range(ALTURA):
            super_sample = [
                inside(x+0.33, y+0.33, vertices),
                inside(x+0.33, y+0.66, vertices),
                inside(x+0.66, y+0.33, vertices),
                inside(x+0.66, y+0.66, vertices),
            ]
            percent = 0

            for sample in super_sample:
                if sample:
                  percent += 0.25

            if percent:
                gpu.GPU.set_pixel(x, y, rgb_color[0]*percent, rgb_color[1]*percent, rgb_color[2]*percent)

LARGURA = 30
ALTURA = 20

if __name__ == '__main__':

    # Valores padrão da aplicação
    width = LARGURA
    height = ALTURA
    x3d_file = "exemplo1.x3d"
    image_file = "tela.png"

    # Tratando entrada de parâmetro
    parser = argparse.ArgumentParser(add_help=False)   # parser para linha de comando
    parser.add_argument("-i", "--input", help="arquivo X3D de entrada")
    parser.add_argument("-o", "--output", help="arquivo 2D de saída (imagem)")
    parser.add_argument("-w", "--width", help="resolução horizonta", type=int)
    parser.add_argument("-h", "--height", help="resolução vertical", type=int)
    parser.add_argument("-q", "--quiet", help="não exibe janela de visualização", action='store_true')
    args = parser.parse_args() # parse the arguments
    if args.input: x3d_file = args.input
    if args.output: image_file = args.output
    if args.width: width = args.width
    if args.height: height = args.height

    # Iniciando simulação de GPU
    gpu.GPU(width, height, image_file)

    # Abre arquivo X3D
    scene = x3d.X3D(x3d_file)
    scene.set_resolution(width, height)

    # funções que irão fazer o rendering
    x3d.X3D.render["Polypoint2D"] = polypoint2D
    x3d.X3D.render["Polyline2D"] = polyline2D
    x3d.X3D.render["TriangleSet2D"] = triangleSet2D

    # Se no modo silencioso não configurar janela de visualização
    if not args.quiet:
        window = interface.Interface(width, height)
        scene.set_preview(window)

    scene.parse() # faz o traversal no grafo de cena

    # Se no modo silencioso salvar imagem e não mostrar janela de visualização
    if args.quiet:
        gpu.GPU.save_image() # Salva imagem em arquivo
    else:
        window.image_saver = gpu.GPU.save_image # pasa a função para salvar imagens
        window.preview(gpu.GPU._frame_buffer) # mostra janela de visualização
