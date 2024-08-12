import csv

class ONI:
    
    def extrair_dados(self):
        dados = []
        first_line = ''
        with open('../ONI.csv', 'r') as file:
            for line in file:
                
                if 'year' in line.lower():
                    first_line = line.replace('\n', '')
                    continue
                
                valores = line.replace('\n', '').split(',')
                year = int(valores[0])
                valores = [float(valores[i]) if valores[i] != '' else 0.0 for i in range(0, len(valores))]
                dados.append(valores)
                
        with open('../oni.csv', 'w') as file:
            csv_writer = csv.writer(file)
            
            csv_writer.writerow(first_line)
            
            for row in dados:
                csv_writer.writerow(row)
        