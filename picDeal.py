from detect import wordSearch
import numpy as np
import cv2
import time




# 坐标转换
def cvt_pos(pos, cvt_mat_t):
    u = pos[0]
    v = pos[1]
    x = (cvt_mat_t[0][0] * u + cvt_mat_t[0][1] * v + cvt_mat_t[0][2]) / (
            cvt_mat_t[2][0] * u + cvt_mat_t[2][1] * v + cvt_mat_t[2][2])
    y = (cvt_mat_t[1][0] * u + cvt_mat_t[1][1] * v + cvt_mat_t[1][2]) / (
            cvt_mat_t[2][0] * u + cvt_mat_t[2][1] * v + cvt_mat_t[2][2])
    return (int(x), int(y))

def CalcEuclideanDistance(point1,point2):
    vec1 = np.array(point1)
    vec2 = np.array(point2)
    distance = np.linalg.norm(vec1 - vec2)
    return distance
#计算第四个点
def CalcFourthPoint(point1,point2,point3): #pint3为A点
    D = (point1[0]+point2[0]-point3[0],point1[1]+point2[1]-point3[1])
    return D
#三点构成一个三角形，利用两点之间的距离，判断邻边AB和AC,利用向量法以及平行四边形法则，可以求得第四个点D
def JudgeBeveling(point1,point2,point3):
    dist1 = CalcEuclideanDistance(point1,point2)
    dist2 = CalcEuclideanDistance(point1,point3)
    dist3 = CalcEuclideanDistance(point2,point3)
    dist = [dist1, dist2, dist3]
    max_dist = dist.index(max(dist))
    if max_dist == 0:
        D = CalcFourthPoint(point1,point2,point3)
    elif max_dist == 1:
        D = CalcFourthPoint(point1,point3,point2)
    else:
        D = CalcFourthPoint(point2,point3,point1)
    return D

def confirmLocPoint(locPointList):
    dis = 0
    num = 0
    for i in range(3):
        j = 0 if i == 2 else i + 1
        tmp = pow(pow(locPointList[i][0] - locPointList[j][0], 2) + pow(locPointList[i][1] - locPointList[j][1], 2),
                  0.5)
        if (tmp > dis):
            dis = tmp
            num = 2 if i == 0 else i - 1
    leftUp = locPointList[num]
    locPointList.pop(num)
    midPoint = [int((locPointList[0][0] + locPointList[1][0]) / 2),int((locPointList[0][1] + locPointList[1][1]) / 2)]
    vetMid = [midPoint[0]-leftUp[0],midPoint[1]-leftUp[1]]
    vetRUp = [locPointList[0][0]-leftUp[0],locPointList[0][1]-leftUp[1]]
    flag = vetMid[0]*vetRUp[1]-vetRUp[0]*vetMid[1]
    if(flag < 0):
        rightUp = locPointList[0]
        leftDown = locPointList[1]
    else:
        leftDown = locPointList[0]
        rightUp = locPointList[1]
    rightDown = JudgeBeveling(leftDown,leftUp,rightUp)
    # rightDown = [int((leftDown[0] / leftUp[0]) * rightUp[0]),int((leftDown[1] / leftUp[1]) * rightUp[1])]
    return [leftUp,leftDown,rightUp,rightDown]


def pointFind(picPath):
    img = cv2.imread(picPath)
    resArr = wordSearch(source=picPath)
    print(resArr)
    flag = 0
    gmLoc = []
    pointLoc = []  # 三个定位点的方框坐标
    crossLoc = []  # 数据点的方框坐标
    pointCenLoc = []  # 三个定位点的中心坐标
    crossCenLoc = []  # 数据点的中心坐标
    pointResStr = ""
    for i in range(len(resArr)):
        if (int(resArr[i][5]) == 0):
            gmLoc.append((int(resArr[i][0]), int(resArr[i][1]), int(resArr[i][2]), int(resArr[i][3])))
        elif (int(resArr[i][5]) == 1):
            pointLoc.append((int(resArr[i][0]), int(resArr[i][1]), int(resArr[i][2]), int(resArr[i][3])))
            flag += 1
        elif (int(resArr[i][5]) == 2):
            crossLoc.append((int(resArr[i][0]), int(resArr[i][1]), int(resArr[i][2]), int(resArr[i][3])))
    if (len(gmLoc)<1 or flag != 3):
        return 0
        # print("检测失败，请重新拍摄。")
    else:
        # 将十字框位置转成中心点坐标存储
        for locitem in pointLoc:
            pointItem = (int((locitem[0] + locitem[2]) / 2), int((locitem[1] + locitem[3]) / 2))
            pointCenLoc.append(pointItem)
        # print(pointCenLoc)
        for msgitem in crossLoc:
            msgPoint = (int((msgitem[0] + msgitem[2]) / 2), int((msgitem[1] + msgitem[3]) / 2))
            crossCenLoc.append(msgPoint)
        # print(crossCenLoc)
        # 找出左上，右上，左下三个点坐标
        leftUp, leftDown, rightUp, rightDown = confirmLocPoint(pointCenLoc)
        # print(leftUp, leftDown, rightUp, rightDown)
        pts1 = np.float32([(42, 34), (138, 34), (138, 146), (42, 146)])  # 预期的棋盘四个角的坐标
        pts2 = np.float32([(leftUp[0], leftUp[1]), (rightUp[0], rightUp[1]), (rightDown[0], rightDown[1]),
                           (leftDown[0], leftDown[1])])  # 当前找到的棋盘四个角的坐标
        # print(leftUp, leftDown, rightUp)
        m = cv2.getPerspectiveTransform(pts2, pts1)  # 生成透视矩阵
        imgCut = cv2.warpPerspective(img, m, (720, 720))  # 对彩色图执行透视变换
        savePicName = "cutPic/" + str(int(time.time())) + ".png"
        cv2.imwrite(savePicName, imgCut)
        # cv2.imshow("img",imgCut)
        # cv2.waitKey()

        poiResArr = np.zeros(14)
        for pointItem in crossCenLoc:
            pointLocTran = cvt_pos(pointItem, m)
            # print(pointLocTran)
            poiX = pointLocTran[0]
            poiY = pointLocTran[1]
            if(poiX<90 and poiY<35):
                poiResArr[0]=poiResArr[0]+1
            elif(poiX>90 and poiY<35):
                poiResArr[1]=poiResArr[1]+1
            elif(poiX<65 and 35<poiY<61):
                poiResArr[2]=poiResArr[2]+1
            elif(65<poiX<115 and 35<poiY<61):
                poiResArr[3]=poiResArr[3]+1
            elif(115<poiX and 35<poiY<61):
                poiResArr[4]=poiResArr[4]+1
            elif(poiX<88 and 61<poiY<90):
                poiResArr[5]=poiResArr[5]+1
            elif(88<poiX and 61<poiY<90):
                poiResArr[6]=poiResArr[6]+1
            elif(poiX<90 and 90<poiY<118):
                poiResArr[7]=poiResArr[7]+1
            elif(90<poiX and 90<poiY<118):
                poiResArr[8]=poiResArr[8]+1
            elif(poiX<65 and 118<poiY<144):
                poiResArr[9]=poiResArr[9]+1
            elif(65<poiX<115 and 118<poiY<144):
                poiResArr[10]=poiResArr[10]+1
            elif(115<poiX and 118<poiY<144):
                poiResArr[11]=poiResArr[11]+1
            elif(poiX<89 and 144<poiY):
                poiResArr[12]=poiResArr[12]+1
            elif(89<poiX and 144<poiY):
                poiResArr[13]=poiResArr[13]+1

        for i in range(len(poiResArr)):
            pointResStr = pointResStr + str(int(poiResArr[i]))
        print(pointResStr)
        return pointResStr