# -*- coding:utf-8 -*-
import shapefile
import os

def read_shp_mul(shp_path,shp_name):
    """ 读取shp文件的类型和点坐标信息

    Args:
        shp_path: shp文件的绝对路径

    Return:
        result: dict类型，整个规划图所有多边形的信息
    """
    print('进入----------------------》》》',shp_path)
    print(shp_name)
    try:
        # 读取shp文件
        file_shp = shapefile.Reader(shp_path,encoding='ISO-8859-1')

        # 读取图像的类型
        type = file_shp.shapeTypeName.capitalize()

        # 读取shp图像的所有点坐标
        shapes = file_shp.shapes()
        result = dict()
        result["geometry"] = []

        for geometry in shapes:
            temp = dict()
            temp["type"] = type
            temp["coordinates"] = list()
            temp["coordinates"].append(
                [list(point) for point in geometry.points])
            result["geometry"].append(temp)
        filename = shp_name + '.txt'
        if(os.path.exists(filename)):
            os.remove(filename)
        os.mknod(filename)

        with open(filename,'w') as f:
            f.write(str(result))

        return result
    except Exception as e:
        print(e)
