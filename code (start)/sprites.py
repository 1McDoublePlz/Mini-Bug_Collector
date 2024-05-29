from settings import *

class Sprite(pygame.sprite.Sprite):
    def __init__(self,pos,surf,groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(topleft = pos)


class AnimatedSprite(Sprite):
    def __init__(self,pos,surf,groups):
        super().__init__(pos, frames[0], groups)