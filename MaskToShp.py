# -*- coding: utf-8 -*-
# @Time    : 2019/11/19 10:02
# @Author  : zhangym
# @FileName: MaskToShp.py
# @Software: PyCharm
# @CSDNblogs ：https://blog.csdn.net/weixin_38834436

import os
import pyproj
import cv2
import gdal
import glob
from shparray import read_shp_mul
from skimage import measure
from transpolygon import download_shpfile

def edge_coords(zuizhong_path,txt_name):
    '''边缘信息'''
    try:
        groundtruth = cv2.imread(zuizhong_path)[:, :, 0]
        contours, cnt= cv2.findContours(groundtruth.copy(),cv2.RETR_TREE ,
                                         cv2.CHAIN_APPROX_NONE)
        with open(txt_name + "_edge.txt","w") as f:
            f.write(str(contours).strip())
        return contours 
    except Exception as ex:
        print(ex)
        return False

def Analysis_Mask(images_path,tiff_path):
    '''
    :param images_path:mask图文件夹路径
    :return: 边缘行列号的数组信息
    '''
    for img_item in os.listdir(images_path):
       #open
        print('开始执行：',img_item)
        original_img = cv2.imread(os.path.join(images_path, img_item),cv2.IMREAD_GRAYSCALE)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(3,3))
        opened = cv2.morphologyEx(original_img, cv2.MORPH_OPEN, kernel,iterations=1)
        cv2.imwrite(os.path.join(images_path, img_item),opened)
        edge_info = edge_coords(os.path.join(images_path, img_item),img_item.split('.')[0])
        print(len(edge_info))
        geotrans = read_img(tiff_path)
        ndegree = []
        for i in range(len(edge_info)):
            yizu = edge_info[i]
            nyizu_piex = []
            for j in range(len(yizu)):
                yizu_piex = [yizu[j][0]][0]
                nyizu_piex.append([yizu_piex[1], yizu_piex[0]])
                
            shp_info = coordinate(nyizu_piex,geotrans)
            
            #print(ndegree.append(shp_info))
            #degree = transpolygon(shp_info)  # 这里要注意列表的维度是两维还是三维
            ndegree.append(shp_info)
 
        shp_type = "Polygon"
        shp_name = img_item.split('.')[0]
        shp_coordinates = ndegree
        with open('./txt/' + shp_name + '.txt','a') as f:
            f.write(str(shp_coordinates))
        shp_path = download_shpfile(shp_type, shp_name, shp_coordinates)   

    pathdir = os.listdir(shp_path)
    for s in pathdir:
        newdir = os.path.join(shp_path,s).replace("\\","/").strip() + '/'
        shp_file = glob.glob(newdir + '*.shp')
       # print( glob.glob(newdir + '*.shp'))
       # print(shp_file[0])
        read_shp_mul(shp_file[0],s)






def coordinate(nyizu_piex,geoMatrix):  # 注意行列号不要写反
    '''
    :param images_path:
    :param tiff_path:
    :return:
    '''
    weizhi= nyizu_piex

    ulx = geoMatrix[0]
    uly = geoMatrix[3]
    xDist = geoMatrix[1]

    zuobiao = []
    for i in range(len(weizhi)):
        col = weizhi[i][1]
        raw = weizhi[i][0]
        x = col * xDist + ulx
        y = uly - raw * xDist
        zuobiao.append([x, y])  # 相对于地理坐标系的对应坐标计算
    return zuobiao

#3.读取裁剪后的影像数据
def read_img(filename):

    dataset=gdal.Open(filename)       #打开文件
    im_width = dataset.RasterXSize    #栅格矩阵的列数
    im_height = dataset.RasterYSize   #栅格矩阵的行数
    im_geotrans = dataset.GetGeoTransform()  #仿射矩阵
    print(im_geotrans)
    print("tiff左上的坐标:({}，{})".format(im_geotrans[0],im_geotrans[3]))
    print('像元宽度:{}'.format(im_geotrans[1]),'像元高度：{}'.format(im_geotrans[5]))
    del dataset
    return im_geotrans

if __name__=="__main__":
    images_path = './mask_image/'
    tiff_path = './1.tif'
    Analysis_Mask(images_path,tiff_path)
