#導入模組
import pygame
import math
import time
import random
import numpy as np
import os
import sys
import json

# 讀取json檔
with open('data.json', "r", encoding="utf8") as file:
    data = json.load(file)

#變數設定
fps = data['fps']                           #每秒執行多少次
probability = data['probability']           #生成機率
width = data['width']                       #視窗寬度
height = data['height']                     #視窗高度
block_count = data['block_count']           #視窗邊的方塊數量
if block_count<=0:                          #數字校正
    block_count=10
space_size = width//block_count             #區塊大小
x_block = width//space_size                 #計算寬有多少格
y_block = height//space_size                #計算高有多少格
execute = True                              #執行
run = False                                 #是否運行中

#介面與初始設定
pygame.init()
wireworld = pygame.display.set_mode((width,height))
pygame.display.set_caption('Wireworld')
#圖片導入
icon = pygame.image.load("img/icon.png")
icon.set_colorkey((255,255,255))
#設定icon
pygame.display.set_icon(icon)
clock = pygame.time.Clock()
wireworld.fill(data['color_background'])


#區塊分區與座標設定
space_x_count = math.ceil(width/space_size)
space_y_count = math.ceil(height/space_size)
space_data = np.ndarray(shape=(space_x_count,space_y_count))
for x in range(0,space_x_count):
    for y in range(0,space_y_count):
        space_data[x][y] = False
#電線
electric_wire = np.ndarray(shape=(space_x_count,space_y_count))
for x in range(0,space_x_count):
    for y in range(0,space_y_count):
        electric_wire[x][y] = -2
#暫存區
storage_cache = np.ndarray(shape=(space_x_count,space_y_count))
for x in range(0,space_x_count):
    for y in range(0,space_y_count):
        storage_cache[x][y] = -1

#滑鼠點擊偵測(設置)
def mouse_click_event_setting(mouseX,mouseY):
    block_x_choose = mouseX//space_size
    block_y_choose = mouseY//space_size
    pygame.draw.rect(surface=wireworld, color=data['wire_color'], rect=((block_x_choose*space_size, block_y_choose*space_size),(space_size,space_size)))
    space_data[block_x_choose][block_y_choose]=True
    storage_cache[x][y] = -1
    electric_wire[x][y] = -1

#滑鼠點擊偵測(移除)
def mouse_click_event_remove(mouseX,mouseY):
    block_x_choose = mouseX//space_size
    block_y_choose = mouseY//space_size
    pygame.draw.rect(surface=wireworld, color=data['color_background'], rect=((block_x_choose*space_size, block_y_choose*space_size),(space_size,space_size)))
    space_data[block_x_choose][block_y_choose]=False
    storage_cache[x][y] = -1
    electric_wire[x][y] = -1

#放置電子
def electronic(mouseX,mouseY):
    block_x_choose = mouseX//space_size
    block_y_choose = mouseY//space_size
    if space_data[block_x_choose][block_y_choose] == True and electric_wire[block_x_choose][block_y_choose]==-2:
        electric_wire[block_x_choose][block_y_choose]=-1
    if space_data[block_x_choose][block_y_choose] == True:
        electric_wire[block_x_choose][block_y_choose] = (electric_wire[block_x_choose][block_y_choose])*(-1)
        if electric_wire[block_x_choose][block_y_choose] == 1:
            pygame.draw.rect(surface=wireworld, color=data['electronic'], rect=((block_x_choose*space_size, block_y_choose*space_size),(space_size,space_size)))
        elif electric_wire[block_x_choose][block_y_choose] == -1:
            pygame.draw.rect(surface=wireworld, color=data['wire_color'], rect=((block_x_choose*space_size, block_y_choose*space_size),(space_size,space_size)))

#電流變化控制
def electricity():
    for i in range(0,space_x_count):
        for j in range(0,space_y_count):
            if space_data[i][j] == True:
                electronic_count = 0
                #座標校正
                if i+1 > space_x_count-1:
                    i_up = i
                else:
                    i_up = i+1
                if i-1 < 0:
                    i_down = i
                else:
                    i_down = i-1
                            
                if j+1 > space_y_count-1:
                    j_up = j
                else:
                    j_up = j+1
                if j-1 < 0:
                    j_down = j
                else:
                    j_down = j-1
                #偵測周圍
                if i_up != i and space_data[i_up][j]==True and electric_wire[i_up][j]==1:
                    electronic_count+=1
                if i_down != i and space_data[i_down][j]==True and electric_wire[i_down][j]==1:
                    electronic_count+=1

                if j_up != j and space_data[i][j_up]==True and electric_wire[i][j_up]==1:
                    electronic_count+=1
                if j_down != j and space_data[i][j_down]==True and electric_wire[i][j_down]==1:
                    electronic_count+=1

                if i_up != i and j_up != j and space_data[i_up][j_up]==True and electric_wire[i_up][j_up]==1:
                    electronic_count+=1
                if i_down != i and j_down != j and space_data[i_down][j_down]==True and electric_wire[i_down][j_down]==1:
                    electronic_count+=1

                if i_up != i and j_down != j and space_data[i_up][j_down]==True and electric_wire[i_up][j_down]==1:
                    electronic_count+=1
                if i_down != i and j_up != j and space_data[i_down][j_up]==True and electric_wire[i_down][j_up]==1:
                    electronic_count+=1
                #電子變化
                if electronic_count>=1 and electronic_count<=2 and electric_wire[i][j]==-1:
                    storage_cache[i][j]=1
                if electric_wire[i][j]==1:
                    storage_cache[i][j]=0
                if electric_wire[i][j]==0:
                    storage_cache[i][j]=-1


#隨機
def random_setting():
    for x in range(0,space_x_count):
            for y in range(0,space_y_count):
                number = math.ceil(random.random()*100)
                if number <= probability:
                    space_data[x][y] = True
                    storage_cache[x][y]=-1
                    electric_wire[x][y] = -1
                else:
                    space_data[x][y] = False
                    storage_cache[x][y]=-1
                    electric_wire[x][y] = -2
    #電路狀態
    for i in range(0,space_x_count):
        for j in range(0,space_y_count):
            if space_data[i][j]==True:
                pygame.draw.rect(surface=wireworld, color=data['wire_color'], rect=((i*space_size, j*space_size),(space_size,space_size)))
            elif space_data[i][j]==False:
                pygame.draw.rect(surface=wireworld, color=data['color_background'], rect=((i*space_size, j*space_size),(space_size,space_size)))
    #更新畫面
    pygame.display.update()
    
#清除電線
def clear():
    for x in range(0,space_x_count):
            for y in range(0,space_y_count):
                space_data[x][y] = False
                storage_cache[x][y] = -1
                electric_wire[x][y] = -1
                pygame.draw.rect(surface=wireworld, color=data['color_background'], rect=((x*space_size, y*space_size),(space_size,space_size)))  
    #更新畫面
    pygame.display.update()

#清除電流
def clear_electricity():
    for x in range(0,space_x_count):
            for y in range(0,space_y_count):
                if space_data[x][y] == True:
                    storage_cache[x][y] = -1
                    electric_wire[x][y] = -1
                    pygame.draw.rect(surface=wireworld, color=data['wire_color'], rect=((x*space_size, y*space_size),(space_size,space_size)))
    #更新畫面
    pygame.display.update()

   
#遊戲執行
while execute:
    clock.tick(fps)
    #按鍵偵測
    for event in pygame.event.get():
        #離開遊戲
        if event.type == pygame.QUIT:
            pygame.quit()
            break
        #設置電線
        if event.type == pygame.MOUSEBUTTONDOWN:
            #偵測滑鼠按下
            mouse_click_type = pygame.mouse.get_pressed()
            if mouse_click_type[0]:
                mouseX,mouseY = pygame.mouse.get_pos()
                if mouseX <= width and mouseY < height and mouseX >= 0 and mouseY >= 0:
                    mouse_click_event_setting(mouseX,mouseY)
        elif event.type == pygame.MOUSEMOTION:
            #偵測滑鼠按下
            mouse_click_type = pygame.mouse.get_pressed()
            if mouse_click_type[0]:
                mouseX,mouseY = pygame.mouse.get_pos()
                if mouseX <= width and mouseY < height and mouseX >= 0 and mouseY >= 0:
                    mouse_click_event_setting(mouseX,mouseY)
        #清除電線
        if event.type == pygame.MOUSEBUTTONDOWN:
            #偵測滑鼠按下
            mouse_click_type = pygame.mouse.get_pressed()
            if mouse_click_type[2]:
                mouseX,mouseY = pygame.mouse.get_pos()
                if mouseX <= width and mouseY < height and mouseX >= 0 and mouseY >= 0:
                    mouse_click_event_remove(mouseX,mouseY)
        elif event.type == pygame.MOUSEMOTION:
            #偵測滑鼠按下
            mouse_click_type = pygame.mouse.get_pressed()
            if mouse_click_type[2]:
                mouseX,mouseY = pygame.mouse.get_pos()
                if mouseX <= width and mouseY < height and mouseX >= 0 and mouseY >= 0:
                    mouse_click_event_remove(mouseX,mouseY)
        #鍵盤偵測
        if event.type == pygame.KEYDOWN:
            #放電子
            if event.key == pygame.K_LCTRL:
                mouseX,mouseY = pygame.mouse.get_pos()
                if mouseX <= width and mouseY < height and mouseX >= 0 and mouseY >= 0:
                    electronic(mouseX,mouseY)
            #離開遊戲
            if event.key == pygame.K_ESCAPE:
                run = False
                execute = False
                pygame.quit()
                break
            #執行隨機設置電線
            if event.key == pygame.K_TAB:
                run = False
                random_setting()
            #清除電線
            if event.key == pygame.K_DELETE:
                run = False
                clear()
            #清除電流
            if event.key == pygame.K_LALT:
                run = False
                clear_electricity()
            #控制是否要運行
            if event.key == pygame.K_SPACE:
                run = not run
    #電流變化控制
    if run == True:     
        electricity()
        #電流控制
        for x in range(0,space_x_count):
            for y in range(0,space_y_count):
                if space_data[x][y]==True:
                    electric_wire[x][y] = storage_cache[x][y]
                    if electric_wire[x][y] == 1:
                        pygame.draw.rect(surface=wireworld, color=data['electronic'], rect=((x*space_size, y*space_size),(space_size,space_size)))
                    if electric_wire[x][y] == -1:
                        pygame.draw.rect(surface=wireworld, color=data['wire_color'], rect=((x*space_size, y*space_size),(space_size,space_size)))
                    if electric_wire[x][y] == 0:
                        pygame.draw.rect(surface=wireworld, color=data['electronic_tail'], rect=((x*space_size, y*space_size),(space_size,space_size)))
        for x in range(0,space_x_count):
            for y in range(0,space_y_count):
                if space_data[x][y]==False:
                    electric_wire[x][y] = -2
                    pygame.draw.rect(surface=wireworld, color=data['color_background'], rect=((x*space_size, y*space_size),(space_size,space_size)))
    
    #畫格子
    for line in range(0,width+1,space_size):
        pygame.draw.line(wireworld , data['line_color'], (line,0), (line,height))
    for line in range(0,height+1,space_size):
        pygame.draw.line(wireworld , data['line_color'], (0,line), (width,line))
    #更新畫面
    pygame.display.update()