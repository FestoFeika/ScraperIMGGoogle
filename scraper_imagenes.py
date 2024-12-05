from selenium import webdriver#para controlar el navegador
from selenium.webdriver.common.by import By #para buscar elementos
from selenium.webdriver.support.ui import WebDriverWait #para esperar a que se carguen las imagenes
from selenium.webdriver.support import expected_conditions as EC #para esperar a que se carguen las imagenes
import time
import os
import requests #para descargar las imagenes


def scraper_imagenes():
    carpeta_destino = r"Carpeta_Imagenes"
    os.makedirs(carpeta_destino, exist_ok=True)
    contador = 1 #numero de la imagen por si ya tienes más de 1
    
    driver = webdriver.Chrome()
    driver.maximize_window()
    
    try:
        driver.get("https://www.google.com/imghp")#entrar a google imagenes
        time.sleep(2)
        
        search_box = driver.find_element(By.NAME, "q")#buscar el cuadro de busqueda
        search_box.send_keys("gatos")#escribir gatos
        search_box.submit()#buscar
        time.sleep(5)
        
        imagenes_info = set() #guarda la URL para que no se repita
        
        for scroll in range(1):
            print(f"\nScroll {scroll + 1}/10")#saber que scroll vamos
            
            try:
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")#para hacer scroll hacia abajo
                time.sleep(3)  # Esperamos que carguen las imágenes
                
                # Esperamos que la imagen cargue completamente
                WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, "img.YQ4gaf"))#busca las imagenes en el "F12"
                )
                
                imagenes_js = driver.execute_script("""
                    return Array.from(document.querySelectorAll('img.YQ4gaf')).filter(img => {
                        return img.naturalWidth > 100 && img.naturalHeight > 100;
                    }).map(img => img.src);
                """)#conseguimos la url con un codigo de java para imagenes grandes (no logos de paginas)
                
                print(f"Encontradas {len(imagenes_js)} imágenes en este scroll")#saber cuantas imagenes encontro
                
                for img_url in imagenes_js:
                    if img_url and img_url not in imagenes_info:  # Si encontró URL y no está duplicada
                        imagenes_info.add(img_url)  # Agrega la URL al conjunto
                        print(f"URL encontrada: {img_url[:50]}...")  # Muestra los primeros 50 caracteres de la URL

            except Exception as e:
                print(f"Error en scroll: {str(e)}")
                break

        print(f"\nComenzando descarga de {len(imagenes_info)} imagenes") #solo como aviso de cuantas imagenes se van a descargar
        for img_url in imagenes_info:
            try:
                print(f"\nDescargando imagen {contador}")
                
                if img_url.startswith('data:image'):
                    import base64 # Para imágenes en base64 (imagenes en binarios)
                    img_data = img_url.split(',')[1]# Extraemos el contenido base64 (quitamos el header)
                    img_bytes = base64.b64decode(img_data)# Decodificamos el base64 a bytes
                    
                    ruta_imagen = os.path.join(carpeta_destino, f"Imagen{contador}.jpg")
                    with open(ruta_imagen, 'wb') as f:
                        f.write(img_bytes)
                else:
                    # Para URLs normales
                    response = requests.get(img_url, timeout=10)
                    if response.status_code == 200:
                        ruta_imagen = os.path.join(carpeta_destino, f"Imagen{contador}.jpg")
                        with open(ruta_imagen, 'wb') as f:
                            f.write(response.content)
                
                print(f"Guardado como Imagen{contador}")
                contador += 1
                time.sleep(1)
                
            except Exception as e:
                print(f"Error con imagen {contador}: {str(e)}")
                continue

    except Exception as e:
        print(f"Error general: {str(e)}")
    
    finally:
        if 'driver' in locals():
            driver.quit()

if __name__ == "__main__":
    scraper_imagenes()