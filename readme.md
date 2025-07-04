## Köşe Tespiti ve Perspektif Düzeltme Uygulaması
- Bu proje, OpenCV kullanarak bir belgeyi (ör. A4 kağıdı) fotoğraftan algılar ve perspektif düzeltme işlemi uygular. Amaç, eğik çekilmiş bir belgeyi kuş bakışı görünümüne dönüştürerek “tarayıcıdan çıkmış” gibi bir görüntü elde etmektir.

## Adımlar
- Görüntüyü yükler ve bulanıklaştırır.
- Canny algoritması ile kenarları tespit eder.
- ```cv.findContours()``` fonkisyonu ile konturlar tespit edilir.
- A4 kağıdı konturunu cv.
- Kağıt konturunu arar ```cv.approxPolyDP()``` fonksiyonu ile köşe sayısını, ```cv.contourArea()``` fonksiyonu ile de kapladığı alanı kontrol eder.
- ```cv.approxPolyDP()``` fonksiyonu ile alınan köşe noktalarını çizip "corner.jpg" olarak dosya dizinine kaydeder.
- Perspektif düzenlemesi için bulunan köşe noktalarını sag ve sol üst, sol ve sağ alt olarak sıraya koyar.
- ```cv.getPerspectiveTransform``` fonskiyonu ile perspektif dönüşüm matrisini hesaplayıp cv.warpPerspective ile perspektif dönüşümünü yapar.

##  Önemli Fonksiyonlar ve Parametreler
- ```cv.GaussianBlur(src, ksize, sigmaX)``` -> Görüntüyü bulanıklaştırır ve gürültüyü azaltır.
Parametreler:
    src: Giriş görüntüsü
    ksize: Çekirdek boyutu (örn. (5,5))
    sigmaX: X yönünde standart sapma

- ```cv.Canny(image, threshold1, threshold2)``` -> Görüntüdeki kenarları tespit eder.
Parametreler: 
    threshold1: Alt eşik değeri
    threshold2: Üst eşik değeri
    Not: threshold1 küçük detayları belirler, threshold2 güçlü kenarları belirler.

- ```cv.findContours(image, mode, method)``` -> Görüntüdeki konturları bulur.
Parametreler:
    mode: Kontur alma modu (cv.RETR_EXTERNAL sadece dış konturları alır)
    method: Kontur basitleştirme algoritması (cv.CHAIN_APPROX_SIMPLE)

- ```cv.approxPolyDP(curve, epsilon, closed)``` -> Kontur üzerindeki noktaları basitleştirir.
Parametreler:
    curve: Kontur noktaları
    epsilon: Maksimum sapma (küçük değer daha hassas)
    closed: Konturun kapalı olup olmadığı (True/False)

- ```cv.getPerspectiveTransform(srcPoints, dstPoints)``` -> Perspektif dönüşüm matrisi hesaplar.

- ```cv.warpPerspective(src, M, dsize)``` -> Görüntüye perspektif dönüşümü uygular.
Parametreler:
    src: Giriş görüntüsü
    M: Perspektif dönüşüm matrisi
    dsize: Çıkış görüntüsünün boyutu    

## Kod Açıklaması
```
import cv2 as cv
import numpy as np

class CamScanner():
    
    def __init__(self):
        # Görüntü okunur ve kenar tespitinde daha temiz sonuç için bulanıklaştırılır.
        self.img = cv.imread("ornek.jpg")
        self.img_blur = cv.GaussianBlur(self.img, (5,5), 0)
    
    def corner(self):
        # Canny ile kenarlar tespit edilir.
        cny = cv.Canny(self.img_blur, 50, 150)
        # Canny'nin tespit ettiği kenarlara konturlar çizilir.
        contours, _ = cv.findContours(cny, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

        for cnt in contours:
            # aproxPolyDP nin hata payı hesaplaması için çevre alınır.
            per = cv.arcLength(cnt, True)
            # Kontur sadeleştirilir, köşe noktalar alınır.
            kenar = cv.approxPolyDP(cnt, per*0.02, True)
            # Konturunu alanı hesaplanır.
            area = cv.contourArea(cnt)
            img2 = self.img.copy()
            # Eğer 4 köşe varsa ve alan 2000 pikselden büyükse konturu seç.
            if len(kenar) == 4 and area > 2000:
                # Hesaplanan köşe noktaları koordinatlarını işaretle
                for point in kenar:
                    x, y = point[0]
                    cv.circle(img2, (x, y), 5, (0, 0, 255), -1)  
                    cv.imwrite("corners.jpg", img2) 
        
                print("Köşeler tespit edildi ve corners.jpg olarak kaydedildi")
                self.corner_sort(kenar)

    #Perspektif dönüşümü için köşe noktaları hesaplaması
    def corner_sort(self, kenar):  
        min_top = 9999
        max_top = 0
        for point in kenar:
            x,y = point[0]
            # x ve y'nin toplamının en küçük olduğu nokta sol üst köşedir.
            if abs(x+y) < min_top:
                sol_ust = (x,y)
                min_top = (x+y)
            # x ve y'nin toplamının en büyük olduğu nokta sağ alt köşedir.
            if (x+y) > max_top:
                sag_alt = (x,y)
                max_top = (x+y)

        min_fark = 9999
        max_fark = 0
        for point in kenar:
            x,y = point[0]
            y-x farkının en küçük olduğu nokta sağ üst köşedir.
            if (y-x) < min_fark:
                sag_ust = (x,y)
                min_fark = (y-x)
            y-x farkının en büyük olduğu nokta sol alt köşedir.
            if (y-x) > max_fark:
                sol_alt = (x,y)
                max_fark = (y-x)    
        self.perspective(sol_ust, sag_ust, sag_alt, sol_alt)
    
    def perspective(self,sol_ust, sag_ust, sag_alt, sol_alt ):
        # Köşe noktaları perspektif matrisi hesaplaması için alınır.
        src_pts = np.float32([sol_ust, sag_ust, sag_alt, sol_alt])
        # Dönüşüm sonrası oluşacak görüntünün boyutu alınır.
        dst_pts = np.float32([[0, 0], [500, 0], [500, 700], [0, 700]])
        
        # Perspektif matirsi hesaplanır.
        matrix = cv.getPerspectiveTransform(src_pts, dst_pts)
        # Matris kullanılarak perspektif dönüşümü yapılır.
        warped = cv.warpPerspective(self.img, matrix, (500, 700))

        # Dönüşüm yapılan görüntü kaydedilir.
        cv.imwrite("warped.jpg", warped)
        print("Perspektif dönüşümü tamamlandı ve 'warped.jpg' olarak kaydedildi.")



if __name__ == "__main__":
    run = CamScanner()
    run.corner()

    
