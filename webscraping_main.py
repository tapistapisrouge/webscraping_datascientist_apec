# -*- coding: utf-8 -*-
"""
Created on Tue Sep 21 16:19:45 2021
@author: amaur
Objectifs :
    - récupérer les offres sur différentes pages web (infos basiques : titre, cdd/cdi, date de début)
    - Mettre en forme les données
    - Comparer les offres aux offres attrappées du dernier lancement de script
    - Extraire les nouvelles offres du jour ! :)
"""

#==============================================================================================
# Modules/Packages à importer =================================================================
#==============================================================================================

import re # inutile ici
import pandas as pd #gestion des dataframes
import pathlib # gestion des chemins
import time #pour attendre à l'ouverture de certaines pages web
import matplotlib.pyplot as plt #visualisation rapide, histogramme


# requests ==> lancer une requête web type "GET une page web" ou un POST
# requests ==> pour faire les requêtes web et chopper les pages sont format html
import requests # non utilisé ici
#from requests_html import HTMLSession
#from requests_html import AsyncHTMLSession # gestion javascript

# bs4 ==> transformer les pages en objet soup et chercher rapidement les infos voulues des différentes balises
from bs4 import BeautifulSoup

# Selenium : permet de lancer un navigateur headless, intéragir avec la page (cliquer sur un boutou etc)
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException



#==============================================================================================
# Chemin absolu à modifier si changement de dossier ou de pc===================================
#==============================================================================================
path_project='C:/Users/Antedis/Documents/APE_2022/python_projects/webscrapping_datascientist'

path_pdf=path_project + "/pdf"

path_csv = path_project + "/output"

path_webdriver = path_project + "/webdriver"


path_firefox = path_webdriver + "/geckodriver.exe"
path_chrome = path_webdriver + "/chromedriver.exe"


#==============================================================================================
# Dataframe de base ===========================================================================
#==============================================================================================

# dataframe stockant les infos 
bdd_datascientist = pd.DataFrame(columns=['organisme',
                                      'salaire',
                                      'trailer',
                                      'CDI_CDD',
                                      'lieu',
                                      'experience'])

#==============================================================================================
# Config des webdriver ========================================================================
#==============================================================================================

# configure Chrome Webdriver
def configure_chrome_driver():
    # Add additional Options to the webdriver
    chrome_options = ChromeOptions()
    # add the argument and make the browser Headless.
    chrome_options.add_argument("--headless")
    # Mettre une taille de fenêtre : technique pour ne pas être considéré comme un bot ?
    chrome_options.add_argument("--window-size=1920,1200")
    # Instantiate the Webdriver: Mention the executable path of the webdriver you have downloaded
    # if driver is in PATH, no need to provide executable_path
    driver = webdriver.Chrome(executable_path=path_chrome, options = chrome_options)
    return driver

# configure Firefox Driver
def configure_firefox_driver():
    # Add additional Options to the webdriver
    firefox_options = FirefoxOptions()
    # add the argument and make the browser Headless.
    firefox_options.add_argument("--headless")
    # Mettre une taille de fenêtre : technique pour ne pas être considéré comme un bot ?
    firefox_options.add_argument("--window-size=1920,1200")
    # Instantiate the Webdriver: Mention the executable path of the webdriver you have downloaded
    # if driver is in PATH, no need to provide executable_path
    driver = webdriver.Firefox(executable_path = path_firefox, options = firefox_options)
    return driver


#==============================================================================================
# WEB SCRAPING SIVAL =====================================================================
#==============================================================================================

# on lance le driver firefox (chrome si besoin mais préférence pour firefox)
driver = configure_firefox_driver()



# infos url
urlpage_offres_base ='https://www.apec.fr/candidat/recherche-emploi.html/emploi?motsCles=data%20scientist&page=' 

# boucle sur les pages de 0 à 19
for page in range(20):
   urlpage_offres =  'https://www.apec.fr/candidat/recherche-emploi.html/emploi?motsCles=data%20scientist&page=' + str(page)
   print(urlpage_offres)

   # le driver headless va sur la page de recrutement
   driver.get(urlpage_offres)
   time.sleep(2)
        
   # on passe le code html en un objet beautifulsoup pour le traiter facilement
   soup_datascientist = BeautifulSoup(driver.page_source,'html.parser')
    

   ensembles = soup_datascientist.find('div', {'class':'container-result'})
   # lister les éléments des balises div de class:"container-result", 1 élément = une offre   
   offres = soup_datascientist.find('div', {'class':'container-result'}).find_all('div', {'class':'card-body'})
       
   href_offres = soup_datascientist.find_all('a', {'queryparamshandling':'merge'})
    
   i=0
   for offre in offres:
        #offre = offres[0]
        # nom organisme ============================================================================
        organisme = offre.find('p', {'class':'card-offer__company mb-10'}).getText()
        print(organisme)
        # salaire ==================================================================================
        salaire = offre.find('ul', {'class':'details-offer'}).find('li').getText()
        # trailer ==================================================================================
        trailer= offre.find('p', {'class':'card-offer__description mb-15'}).getText()   
        # gloabl fin de la div
        cdi_lieu = offre.find('ul',{'class':'details-offer important-list'}).find_all('li')
        # cdd_cdi ==================================================================================
        CDI_CDD = cdi_lieu[0].getText()    
        # lieu ==================================================================================
        lieu = cdi_lieu[1].getText()    
        
        # lien plus d'infos ============================================================================
        href_offre = href_offres[i].get('href')
        href_finale = 'https://www.apec.fr' + href_offre
        print(href_finale)   
        # on va sur la page de l'offre
        driver.get(href_finale)
        time.sleep(2)
        soup_temp = BeautifulSoup(driver.page_source,'html.parser')
        
        # infos experiences necessaires
        experience = soup_temp.find_all('div',{'class':'details-post'})[2].find('span').getText()
        
    
        # on enregistre les infos
        bdd_datascientist =  bdd_datascientist.append({'organisme':organisme,
                                                       'salaire':salaire,
                                                       'trailer':trailer,
                                                       'CDI_CDD':CDI_CDD,
                                                       'lieu':lieu,
                                                       'experience':experience},
                                                      ignore_index=True
                                                      )    
        # on incrémente
        i=i+1
        print(i)
        
        
        
driver.quit()



#==============================================================================================
# Gestion du csv ==============================================================================
#==============================================================================================

csv_synthese = 'bdd_datascientist.csv'
path_csv_synthese = pathlib.Path(path_csv, csv_synthese)

# verif son existence, puis enregistrement
if pathlib.Path.is_file(path_csv_synthese)==False:
    bdd_datascientist.to_csv(path_csv_synthese, encoding='utf-8-sig', sep=';', decimal='.', index=False)
    
    
#==============================================================================================
# création dataframe salaire/experience ==============================================================================
#==============================================================================================

df_joel_final = pd.read_csv(path_csv_synthese, sep=';', decimal='.')

list_salaires = df_joel_final['salaire'].unique()
list_experiences = df_joel_final['experience'].unique()

# creation df
df_analyse = pd.DataFrame(list_salaires, columns = ['salaires'])

for experience in list_experiences:
    #experience = list_experiences[0]
    df_analyse[experience] = 0 
    # filtrer df par l'experience
    df_temp = df_joel_final[df_joel_final['experience']==experience]
    for salaire in list_salaires:
        #salaire = list_salaires[5]
        df_temp_salaire = df_temp[df_temp['salaire']==salaire]
        occurrence = df_temp_salaire.shape[0]
        # ajouter l'occurence
        index_list = df_analyse[df_analyse['salaires']==salaire].index.tolist()
        ligne = index_list[0]
        df_analyse.loc[ligne,experience] = occurrence       
    

# df avec juste occurrence des salaires
# creation df
df_analyse_salaire = pd.DataFrame(list_salaires, columns = ['salaires'])
df_analyse_salaire['occurrence'] = 0
for salaire in list_salaires:
    # filtrer df par l'experience
    df_temp = df_joel_final[df_joel_final['salaire']==salaire]
    #salaire = list_salaires[5]
    occurrence = df_temp.shape[0]
    # ajouter l'occurence
    index_list = df_analyse_salaire[df_analyse_salaire['salaires']==salaire].index.tolist()
    ligne = index_list[0]
    df_analyse_salaire.loc[ligne,'occurrence'] = occurrence   
# créer pourcentage
df_analyse_salaire['pourcentage'] = df_analyse_salaire['occurrence']/df_joel_final.shape[0]*100
   

#==============================================================================================
# création histogramme (manip sur exel avant attention ========================================
# flemme de faire certaines manip de chaine de character sur python ===========================
#==============================================================================================
    
#histogramme
csv_histo = 'bdd_datascientist_histo.csv'
path_csv_histo = pathlib.Path(path_csv, csv_histo)
df_histo = pd.read_csv(path_csv_histo, sep=';', decimal='.', encoding='latin-1')

plt.hist(df_histo['salaire mini'], bins = 8)
plt.ylabel('Nombre d\'offre')
plt.xlabel('salaire (k€)')
plt.title('Salaire mini data scientist - 147 offres APEC')
plt.legend()

chemin_histo = pathlib.Path(path_csv, 'histo_datascientist_salairemini.png')
plt.savefig(chemin_histo)


plt.hist(df_histo['salaire maxi'], bins = 20)
plt.ylabel('Nombre d\'offre')
plt.xlabel('salaire (k€)')
plt.title('Salaire maxi data scientist - 147 offres APEC')
plt.legend()

chemin_histo = pathlib.Path(path_csv, 'histo_datascientist_salairemaxi.png')
plt.savefig(chemin_histo)










