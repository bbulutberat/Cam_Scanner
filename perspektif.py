import cv2 as cv
import numpy as np

class CamScanner():
    
    def __init__(self):
        self.img = cv.imread("ornek.jpg")
        self.img_blur = cv.GaussianBlur(self.img, (5,5), 0)
    
    def corner(self):
        cny = cv.Canny(self.img_blur, 50, 150)
        contours, _ = cv.findContours(cny, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

        for cnt in contours:
            per = cv.arcLength(cnt, True)
            kenar = cv.approxPolyDP(cnt, per*0.02, True)
            area = cv.contourArea(cnt)
            img2 = self.img.copy()
            if len(kenar) == 4 and area > 2000:
                for point in kenar:
                    x, y = point[0]
                    cv.circle(img2, (x, y), 5, (0, 0, 255), -1)  
                    cv.imwrite("corners.jpg", img2) 
                    
                print("Köşeler tespit edildi ve corners.jpg olarak kaydedildi")
                self.corner_sort(kenar)
        
    def corner_sort(self, kenar):  
        min_top = 9999
        max_top = 0
        for point in kenar:
            x,y = point[0]
            if abs(x+y) < min_top:
                sol_ust = (x,y)
                min_top = (x+y)
            if (x+y) > max_top:
                sag_alt = (x,y)
                max_top = (x+y)

        min_fark = 9999
        max_fark = 0
        for point in kenar:
            x,y = point[0]
            if (y-x) < min_fark:
                sag_ust = (x,y)
                min_fark = (y-x)
            if (y-x) > max_fark:
                sol_alt = (x,y)
                max_fark = (y-x)    
        self.perspective(sol_ust, sag_ust, sag_alt, sol_alt)
    
    def perspective(self,sol_ust, sag_ust, sag_alt, sol_alt ):
        src_pts = np.float32([sol_ust, sag_ust, sag_alt, sol_alt])
        dst_pts = np.float32([[0, 0], [500, 0], [500, 700], [0, 700]])
        
        matrix = cv.getPerspectiveTransform(src_pts, dst_pts)
        warped = cv.warpPerspective(self.img, matrix, (500, 700))

        cv.imwrite("warped.jpg", warped)
        print("Perspektif dönüşümü tamamlandı ve 'warped.jpg' olarak kaydedildi.")



if __name__ == "__main__":
    run = CamScanner()
    run.corner()

    