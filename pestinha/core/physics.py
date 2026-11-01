"""
PHYSICS - corpo 2D do pet: gravidade, inércia, rotação, quique e pouso.

Coordenadas lógicas do Qt (as mesmas de QCursor.pos()). O corpo é uma
caixa (half_w x half_h) girada pelo ângulo; para colidir usamos a caixa
que envolve o corpo girado. Plataformas são as barras de título das janelas.
"""

import math
from ..ajustes import (
    GRAVIDADE as GRAVITY,
    QUICA as RESTITUTION,
    ATRITO_CHAO as GROUND_FRICTION,
    ARRASTO_AR as AIR_DRAG,
    ARRASTO_GIRO_AR as ANGULAR_DRAG,
    MOLA_ENDIREITAR as RIGHTING_K,
    AMORTECIMENTO_ENDIREITAR as RIGHTING_DAMP,
    GIRO_MAXIMO as MAX_SPIN,
    BOTOES_JANELA as CLOSE_BUTTONS,
)



def wrap_angle(deg):
    """Ângulo em graus, normalizado para o intervalo de -180 a 180."""
    return (deg + 180.0) % 360.0 - 180.0


class Body:
    """Corpo na tela: posição, velocidade, ângulo e contato com as superfícies (chão e janelas)."""
    def __init__(self, x, y, half_w, half_h):
        """Cria o corpo em (x, y), com metade da largura e da altura (para medir o contato)."""
        self.x, self.y = x, y
        self.vx = self.vy = 0.0
        self.angle = 0.0          # graus, 0 = em pé
        self.omega = 0.0          # graus/s
        self.half_w, self.half_h = half_w, half_h
        self.grounded = False
        self.platform = None      # hwnd da janela onde está pousado, ou None (chão)
        self.surface = 0.0        # y da superfície onde está apoiado
        self.impacts = []         # velocidades das batidas desde a última leitura (px/s)
        self.held = False         # sendo segurado pelo mouse

    def pop_impacts(self):
        """Devolve as batidas desde a última vez e zera a lista (para a rede sentir a batida)."""
        out, self.impacts = self.impacts, []
        return out

    def extents(self):
        """Metade da largura e da altura do corpo já girado (para saber onde a base encosta)."""
        a = math.radians(self.angle)
        c, s = abs(math.cos(a)), abs(math.sin(a))
        return self.half_w * c + self.half_h * s, self.half_w * s + self.half_h * c

    def resting_angle(self):
        """Lado mais próximo para assentar (0 em pé, ±90 tombado, 180 de ponta-cabeça)."""
        return round(self.angle / 90.0) * 90.0

    def upright(self):
        """Diz se o corpo está em pé (inclinado menos de 30 graus)."""
        return abs(wrap_angle(self.angle)) < 30.0

    def step(self, dt, bounds, platforms):
        """
        bounds: (left, top, right, bottom) da área de trabalho.
        platforms: [(hwnd, left, right, top)] barras de título candidatas.
        """
        if self.held:
            return
        left, top, right, bottom = bounds

        if not self.grounded:
            self.vy += GRAVITY * dt
            self.vx -= self.vx * AIR_DRAG * dt
            self.omega -= self.omega * ANGULAR_DRAG * dt
        else:
            self.vx -= self.vx * GROUND_FRICTION * dt
            target = self.resting_angle()
            self.omega += ((target - self.angle) * RIGHTING_K - self.omega * RIGHTING_DAMP) * dt

        self.omega = max(-MAX_SPIN, min(MAX_SPIN, self.omega))
        self.angle += self.omega * dt
        if abs(self.angle) > 3600:
            self.angle = wrap_angle(self.angle)

        ex, ey = self.extents()
        prev_bottom = self.y + ey
        self.x += self.vx * dt
        self.y += self.vy * dt

        # paredes
        if self.x - ex < left:
            self.x = left + ex
            self.impacts.append(abs(self.vx))
            self.vx = abs(self.vx) * RESTITUTION
            self.omega += self.vy * 0.15
        elif self.x + ex > right:
            self.x = right - ex
            self.impacts.append(abs(self.vx))
            self.vx = -abs(self.vx) * RESTITUTION
            self.omega -= self.vy * 0.15
        if self.y - ey < top:
            self.y = top + ey
            self.impacts.append(abs(self.vy))
            self.vy = abs(self.vy) * RESTITUTION

        # apoiado: acompanha a superfície; se ela sumiu/mexeu ou ele saiu da beirada, cai
        if self.grounded:
            surface = bottom
            if self.platform is not None:
                plat = next((p for p in platforms if p[0] == self.platform), None)
                if plat is None or not (plat[1] <= self.x <= plat[2] - CLOSE_BUTTONS) or abs(plat[3] - self.surface) > 4:
                    self.grounded = False
                    self.platform = None
                else:
                    surface = plat[3]
            if self.grounded:
                self.surface = surface
                self.y = surface - ey
                self.vy = 0.0
                return

        # pouso numa barra de título (só caindo, vindo de cima)
        new_bottom = self.y + ey
        if self.vy > 0:
            cruzadas = [(p_top, hwnd) for hwnd, p_left, p_right, p_top in platforms
                        if p_left <= self.x <= p_right - CLOSE_BUTTONS and prev_bottom <= p_top + 2 <= new_bottom + 2
                        and new_bottom >= p_top]
            if cruzadas:
                p_top, hwnd = min(cruzadas)          # a primeira superfície que a queda encontra é a mais alta
                self._land(p_top, ey, hwnd)
                return

        # chão (acima da barra de tarefas)
        if self.y + ey >= bottom:
            self._land(bottom, ey, None)

    def _land(self, surface, ey, platform):
        """Pousa o corpo sobre uma superfície (chão ou janela): para de cair e guarda onde pousou."""
        self.y = surface - ey
        self.surface = surface
        self.impacts.append(abs(self.vy))
        if self.vy > 260:
            self.vy = -self.vy * RESTITUTION
            self.omega += self.vx * 0.4
            return
        self.vy = 0.0
        self.grounded = True
        self.platform = platform

    def jump(self, vx, vy, spin=0.0):
        """Dá um impulso: muda a velocidade e tira o corpo do chão (com giro opcional)."""
        self.grounded = False
        self.platform = None
        self.vx, self.vy = vx, vy
        self.omega += spin
