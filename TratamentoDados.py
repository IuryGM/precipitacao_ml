import pandas as pd
import csv
from sklearn.preprocessing import LabelEncoder

def is_numeric_column(col):
    try:
        pd.to_numeric(col)
        
        return True
    except:
        return False

def extrair_dados_oni():
    
    oni_dict = {}
    
    with open('../ONI.csv') as file:
        reader = csv.reader(file)
        
        for row in reader:
            if 'year' in row[0].lower():
                continue
            year = int(row[0])

            oni_dict[year] = [float(oni) if oni != '' else 0 for oni in row[1:]]
            
    return oni_dict

def adicionar_dados_oni_row(row, oni_dict):
    year = row['year']
    month = row['month']
    return oni_dict[year][month-1]
    
def classificacao_el_nino(row, oni_dict):
    year = row['year']
    month = row['month']
    
    oni = oni_dict[year][month-1]
    
    if oni >= 2.0:
        return 'Very Strong'
    elif oni < 2.0 and oni >= 1.5:
        return 'Strong'
    elif oni < 1.5 and oni >= 1.0:
        return 'Moderate'
    elif oni < 1.0 and oni >= 0.5:
        return 'Weak'
    return 'No'    

def classificacao_la_nina(row, oni_dict):
    year = row['year']
    month = row['month']
    
    oni = oni_dict[year][month-1]

    if oni <= -2.0:
        return 'Very Strong'
    elif oni > -2.0 and oni <= -1.5:
        return 'Strong'
    elif oni > -1.5 and oni <= -1.0:
        return 'Moderate'
    elif oni > -1.0 and oni <= -0.5:
        return 'Weak'
    return 'No'    


def tratar_dataframe_dados_originais(nome_arquivo):
    df = pd.read_csv(nome_arquivo)

    df = df[df['PRECIPITAO TOTAL. HORRIO (mm)'] >= 0]

    for column in df.columns:
        if is_numeric_column(df[column]):
            df[column] = df[column].apply(lambda x : 0 if float(x) < 0 else float(x))

    df['DATA (YYYY-MM-DD)'] = df['DATA (YYYY-MM-DD)'].apply(lambda data : data.replace('/', '-'))
    
    df['DATA (YYYY-MM-DD)'] = pd.to_datetime(df['DATA (YYYY-MM-DD)'])
    
    df['year'] = df['DATA (YYYY-MM-DD)'].dt.year
    df['month'] = df['DATA (YYYY-MM-DD)'].dt.month
    df['day'] = df['DATA (YYYY-MM-DD)'].dt.day

    df['year_month'] = df['DATA (YYYY-MM-DD)'].dt.to_period('M')

    df['HORA (UTC)'] = df['HORA (UTC)'].apply(lambda x : f'{x[0:2:1]}:{x[2:4:1]}' if 'UTC' in x.upper() else x)

    df['hour'] = pd.to_datetime(df['HORA (UTC)'], format='%H:%M').dt.hour

    df = df.rename(columns={
        'DATA (YYYY-MM-DD)': 'year_month_day'
        })

    df.drop(columns=[df.columns[-6], 'HORA (UTC)'], inplace=True)
    
    df = df.reset_index(drop=True)
    oni_dict = extrair_dados_oni()
    #df['ONI'] = df.apply(lambda x : adicionar_dados_oni_row(x, oni_dict), axis=1)

    df['el_nino'] = df.apply(lambda x : classificacao_el_nino(x, oni_dict), axis=1)
    df['la_nina'] = df.apply(lambda x : classificacao_la_nina(x, oni_dict), axis=1)

    return df

def rename_columns(df):
    return df.rename(columns={
        'PRECIPITAO TOTAL. HORRIO (mm)': 'precipitacao',
        'PRESSAO ATMOSFERICA AO NIVEL DA ESTACAO. HORARIA (mB)': 'pressao_atmosferica',
        'RADIACAO GLOBAL (KJ/m)': 'radiacao_global',
        'TEMPERATURA DO AR - BULBO SECO. HORARIA (C)': 'temperatura_do_ar',
        'TEMPERATURA DO PONTO DE ORVALHO (C)': 'temperatura_ponto_orvalho',
        'UMIDADE RELATIVA DO AR. HORARIA (%)': 'umidade',
        'VENTO. DIREO HORARIA (gr) ( (gr))': 'direcao_vento_horario',
        'VENTO. RAJADA MAXIMA (m/s)': 'vento_rajada_maxima',
        'VENTO. VELOCIDADE HORARIA (m/s)': 'vento_velocidade_horaria'
    })


def gerar_daily_dataframe(nome_arquivo):
    df = tratar_dataframe_dados_originais(nome_arquivo)
    
    df = rename_columns(df)
    
    aggregation = {
        'precipitacao': 'sum',
        'pressao_atmosferica': ['mean'],
        'radiacao_global': ['mean'],
        'temperatura_do_ar': ['mean'],
        'temperatura_ponto_orvalho': ['mean'],
        'umidade': ['mean'],
        'direcao_vento_horario': ['mean'],
        'vento_rajada_maxima': ['mean'],
        'vento_velocidade_horaria': ['mean'],
        'year': 'first',
        'month': 'first',
        'day': 'first',
        'la_nina': 'first',
        'el_nino': 'first'
    }
    
    df_grouped = df.groupby('year_month_day')
    daily_df = df_grouped.agg(aggregation).reset_index()
    daily_df['num_observacoes'] = df_grouped.size().values
    daily_df.reset_index()
    daily_df.columns = [
        f"{col[0]}_{col[1]}" if isinstance(col, tuple) else col for col in daily_df.columns
    ]    
    
    daily_df.rename(columns={
        'year_first': 'year', 'month_first': 'month', 'day_first': 'day', 
        'num_observacoes_': 'num_observacoes', 'year_month_day_': 'year_month_day',
        'la_nina_first': 'la_nina', 'el_nino_first': 'el_nino'
        }, inplace=True)
    
    daily_df.rename(columns={
        'precipitacao_sum': 'precipitacao', 'pressao_atmosferica_mean': 'pressao_atmosferica', 'radiacao_global_mean': 'radiacao_global', 
        'temperatura_do_ar_mean': 'temperatura_do_ar', 'temperatura_ponto_orvalho_mean': 'temperatura_ponto_orvalho', 'umidade_mean': 'umidade',
        'direcao_vento_horario_mean': 'direcao_vento_horario', 'vento_rajada_maxima_mean': 'vento_rajada_maxima', 'vento_velocidade_horaria_mean': 'vento_velocidade_horaria'
    }, inplace=True)

    categories = ['No', 'Weak', 'Moderate', 'Strong', 'Very Strong']

    label_encoder = LabelEncoder()

    daily_df['la_nina'] = pd.Categorical(daily_df['la_nina'], categories=categories, ordered=True)
    daily_df['la_nina'] = label_encoder.fit_transform(daily_df['la_nina'])

    encoded_categories = label_encoder.inverse_transform(daily_df['la_nina'])

    categories = ['No', 'Weak', 'Moderate', 'Strong', 'Very Strong']

    label_encoder = LabelEncoder()
    
    daily_df['el_nino'] = pd.Categorical(daily_df['el_nino'], categories=categories, ordered=True)
    daily_df['el_nino'] = label_encoder.fit_transform(daily_df['el_nino'])

    daily_df = daily_df.set_index('year_month_day')
    
    return daily_df