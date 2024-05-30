from settings import *

class Sprite(pygame.sprite.Sprite):
    def __init__(self,pos,surf,groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(topleft = pos)


class AnimatedSprite(Sprite):
    def __init__(self,pos,frames,groups):
        self.frame_index, self.frames = 0, frames
        super().__init__(pos, frames[self.frame_index], groups)

    def animate(self):
        self.frame += 4 * dt
        self.image = self.frames[self.frame_index]