from settings import *
from sprites import MonsterSprite, MonsterNameSprite, MonsterLevelSprite, MonsterStatsSprite, MonsterOutlineSprite, AttackSprite, TimedSprite
from groups import BattleSprites
from game_data import ATTACK_DATA
from support import draw_bar
from timer import Timer
from random import choice

class Battle:
    #main
    def __init__(self,player_monsters, opponent_monsters, monster_frames,bg_surf, fonts, end_battle, character, sounds):
        #general
        self.display_surface = pygame.display.get_surface()
        self.bg_surf = bg_surf
        self.monster_frames = monster_frames
        self.fonts = fonts
        self.monster_data = {'player': player_monsters, 'opponent': opponent_monsters}
        self.battle_over = False
        self.end_battle = end_battle
        self.character = character
        self.sounds = sounds

        #timers
        self.timers = {
            'opponent delay': Timer(600, func=self.opponent_attack)
        }

        #groups
        self.battle_sprites = BattleSprites()
        self.player_sprites = pygame.sprite.Group()
        self.opponent_sprites = pygame.sprite.Group()

        #control
        self.current_monster = None
        self.selection_mode = None
        self.selected_attack = None
        self.selection_side = 'player'
        self.indexes = {
            'general':0,
            'monster':0,
            'attack':0,
            'switch':0,
            'target':0,
        }

        self.setup()

    def setup(self):
        for entity, monster in self.monster_data.items():
            for index, monster in {k:v for k,v in monster.items() if k<=2}.items():
                self.create_monster(monster,index, index, entity)

                #remove opponent monster data 
            for i in range(len(self.opponent_sprites)):
                del self.monster_data['opponent'][i]

    def create_monster(self,monster,index,pos_index,entity):
        monster.paused = False
        frames = self.monster_frames['monsters'][monster.name]
        outline_frames = self.monster_frames['outlines'][monster.name]
        if entity == 'player':
            pos = list(BATTLE_POSITIONS['left'].values())[pos_index]
            groups = (self.battle_sprites, self.player_sprites)
            frames = {state: [pygame.transform.flip(frame, True, False) for frame in frames] for state, frames in frames.items()}
            outline_frames = {state: [pygame.transform.flip(frame, True, False) for frame in frames] for state, frames in outline_frames.items()}
        else:
            pos = list(BATTLE_POSITIONS['right'].values())[pos_index]
            groups = self(self.battle_sprites, self.opponent_sprites)

        monster_sprite = MonsterSprite(pos, frames, groups, monster, index, pos_index, entity, self.apply_attack, self.create_monster)
        MonsterOutlineSprite(monster_sprite, self.battle_sprites, outline_frames)

        #ui
        name_pos = monster_sprite.rect.midleft + vector(16,-70) if entity == 'player' else monster_sprite.rect.midright + vector (-40, -70)
        name_sprite = MonsterNameSprite(name_pos, monster_sprite, self.battle_sprites, self.fonts['regular'])
        level_pos = name_sprite.rect.bottomleft if entity == 'player' else name_sprite.rect.bottomright
        MonsterLevelSprite(entity,level_pos,monster_sprite, self.battle_sprites, self.fonts['small'])
        MonsterStatsSprite(monster_sprite.rect.midbottom + vector(0,20), monster_sprite, (150,48), self.battle_sprites,self.fonts['small'])

    def input(self):
        if self.selection_mode and self.current_monster:
            keys = pygame.key.get_just_pressed()

            match self.selection_mode:
                case 'general': limiter =len(BATTLE_CHOICES['full'])
                case 'attacks': limiter = len(self.current_monster.monster.get_abilities(all = False))
                case 'switch': limiter = len(self.available_monsters)
                case 'target': limiter = len(self.opponent_sprites) if self.selection_side == 'opponent' else len(self.player_sprites)

            if keys[pygame.K_DOWN]:
                self.indexes[self.selection_mode] = (self.indexes[self.selection_mode] + 1) % limiter
            if keys[pygame.K_UP]:
                self.indexes[self.selection_mode] = (self.indexes[self.selection_mode] - 1) % limiter
            if keys[pygame.K_SPACE]:

                if self.selection_mode == 'switch':
                    index, new_monster = list(self.available_monsters.items())[self.indexes['switch']]
                    self.current_monster.kill()
                    self.create_monster(new_monster, index, self.current_monster.pos_index, 'player')
                    self.selection_mode = None
                    self.update_all_monsters('resume')

                if self.selection_mode == 'target':
                    sprite_group = self.opponent_sprites if self.selection_side == 'opponent' else self.player_sprites
                    sprites = {sprite.pos_index: sprite for sprite in sprite_group}
                    monster_sprite = sprites[list(sprites.keys())[self.indexes['target']]]

                    if self.selected_attack:
                        self.current_monster.activate_attack(monster_sprite, self.selected_attack)
                        self.selected_attack, self.current_monster, self.selection_mode = None, None, None
                    else:
                        if monster_sprite.monster.health < monster_sprite.monster.get_stat('max_health') * 0.9:
                            self.monster_data['player'][len(self.monster_data['player'])] = monster_sprite.monster
                            monster_sprite.delayed_kill(None)
                            self.update_all_monsters('resume')
                        else:
                            TimedSprite(monster_sprite.rect.center, self.monster_frames['ui']['cross'], self.batlle_sprites, 1000)

            

                 
