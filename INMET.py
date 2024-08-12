from pathlib import Path

import os
import csv
import json

class INMET:
    
    def __init__(self):
        self._regioes_inmet = {}
        self._path_inmet_str = '../INMET/'
        
    def extrair_dados_inmet(self):
        diretorios = self._extrair_diretorios_inmet()
        
        self._gerar_diretorios_tratados(diretorios)
        self._gerar_geojson_regioes()

    def _gerar_diretorios_tratados(self, diretorios):
        for diretorio in diretorios:
            files = self._list_files(diretorio)
            
            for file in files:
                if 'localiza' in file:
                    continue
                regiao, cidade = self._extrair_regiao_cidade(file)                
                ano = diretorio.split('/')[-2]
                self._criar_diretorio_regiao(regiao)
                self._criar_diretorio_cidade(regiao, cidade)
                
                self._tratar_dados_cidade(file, regiao, cidade, ano)

    def _gerar_geojson_regioes(self):
        for regiao in self._regioes_inmet.keys():
            self._gerar_geojson_regiao(regiao)
            
    def _gerar_geojson_regiao(self, regiao):
        features = []
        
        for cidade, coordinate in self._regioes_inmet[regiao].items():
            properties = {'cidade': cidade}
            geometry = {'type': 'Point', 'coordinates': [coordinate['x'], coordinate['y']]}
            feature = {'type': 'Feature', 'properties': properties, 'geometry': geometry}
            features.append(feature)
            
        with open(f'{self._path_inmet_str}{regiao}/localizacoes.json', 'w') as json_file:
            json.dump({'type': 'FeatureCollection', 'features': features}, json_file)
            
    def _tratar_dados_cidade(self, file, regiao, cidade, ano):
        with open(f'{self._path_inmet_str}{ano}/{file}', 'r', encoding='utf-8', errors='ignore') as file:
            lines = file.readlines()
            
        lines_csv = []
                      
        y = None
        x = None
                        
        for line in lines:
            
            line = line.replace(',', '.')
            
            if not self._regioes_inmet[regiao][cidade]:
                if 'latitude' in line.lower():
                    y = float(line.split(';')[1])
                if 'longitude' in line.lower():
                    x = float(line.split(';')[1])

                if x is not None and y is not None:
                    self._regioes_inmet[regiao][cidade]['x'] = x
                    self._regioes_inmet[regiao][cidade]['y'] = y

            line_splitted = line.split(';')

            if len(line_splitted) > 2:
                lines_csv.append(line_splitted)

        with open(f'{self._path_inmet_str}{regiao}/{cidade}/{ano}.csv', 'w') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerows(lines_csv)

    def _criar_diretorio_regiao(self, regiao):
        if regiao not in self._regioes_inmet.keys():
            self._regioes_inmet[regiao] = {}
                    
            diretorio_regiao = self._diretorio_regiao(regiao)
            if not os.path.exists(diretorio_regiao):
                os.makedirs(diretorio_regiao)
        
    def _criar_diretorio_cidade(self, regiao, cidade):
        if cidade not in self._regioes_inmet[regiao].keys():
            self._regioes_inmet[regiao][cidade] = {}
                    
            diretorio_cidade = self._diretorio_cidade(regiao, cidade)
            if not os.path.exists(diretorio_cidade):
                os.makedirs(diretorio_cidade)
                
    def _extrair_regiao_cidade(self, file):
        file_splitted = file.split('_')
        regiao = file_splitted[2]
        cidade = file_splitted[4]
        return regiao, cidade
                    
    def _diretorio_regiao(self, regiao):
        return f'{self._path_inmet_str}{regiao}/'
        
    def _diretorio_cidade(self, regiao, cidade):
        return f'{self._diretorio_regiao(regiao)}{cidade}/'
        
    def _extrair_diretorios_inmet(self):
        path_inmet = Path(self._path_inmet_str).resolve()
        diretorios = [f'{str(entry)}/' for entry in path_inmet.iterdir() if entry.is_dir()]
        
        return diretorios        
    
    def _list_files(self, diretorio):
        files = []
        for filename in os.listdir(diretorio):
            path = os.path.join(diretorio, filename)
            if os.path.isfile(path):
                files.append(filename)
        return files
    
    