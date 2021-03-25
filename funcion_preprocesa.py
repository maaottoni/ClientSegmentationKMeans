import numpy as np
import pandas as pd

def preprocesa(all_data):
    """
    Funcion de preprocesamiento de los datos, recibe un data frame y lo preprocesa
    """

    # Casteamos las columnas que contienen fechas a datetime
    date_columns = ['order_purchase_timestamp', 'order_approved_at', 'order_delivered_carrier_date', 'order_delivered_customer_date',
                    'order_estimated_delivery_date', 'shipping_limit_date', 'review_creation_date', 'review_answer_timestamp'] 
    convertToDate(all_data, date_columns)
    
    
    #Creamos una columna Month_order para la exploración de datos
    all_data['Month_order'] = all_data['order_purchase_timestamp'].dt.to_period('M').astype('str')
    
    # Nos quedamos con las columnas que van desde 01-2017 hasta 08-2018
    # Porque hay datos que están fuera de balance con el promedio de cada mes en los datos antes del 01-2017 y después del 08-2018
    # basado en datos de compra / order_purchase_timestamp
    start_date = "2017-01-01"
    end_date = "2018-08-31"
    after_start_date = all_data['order_purchase_timestamp'] >= start_date
    before_end_date = all_data['order_purchase_timestamp'] <= end_date
    between_two_dates = after_start_date & before_end_date
    all_data = all_data.loc[between_two_dates]
    
    # Gestión de entradas vacías 
    deleteEmptyEntries(all_data, 'order_approved_at','order_purchase_timestamp')
    deleteEmptyEntries(all_data, 'order_delivered_carrier_date','order_approved_at')
    deleteEmptyEntries(all_data, 'order_delivered_customer_date','order_delivered_carrier_date')
    # El número de entradas en blanco en las columnas review_comment_title y review_comment_message es muy grande 
    # e imposible de completar. La eliminamos
    all_data = all_data.drop(['review_comment_title', 'review_comment_message'], axis=1)
    all_data = all_data.dropna()
   
    # Ajuste el tipo de datos
    int64_columns = ['order_item_id', 'product_name_lenght', 'product_description_lenght', 'product_photos_qty']
    convertToInt64(all_data, int64_columns)
    
    # adición de nuevas columnas que contienen cálculos de varias columnas para obtener una nueva característica
    all_data['order_process_time'] = all_data['order_delivered_customer_date'] - all_data['order_purchase_timestamp']
    all_data['order_delivery_time'] = all_data['order_delivered_customer_date'] - all_data['order_delivered_carrier_date']
    all_data['order_accuracy_time'] = all_data['order_estimated_delivery_date'] - all_data['order_delivered_customer_date'] 
    all_data['order_approved_time'] = all_data['order_approved_at'] - all_data['order_purchase_timestamp'] 
    all_data['review_send_time'] = all_data['review_creation_date'] - all_data['order_delivered_customer_date']
    all_data['review_answer_time'] = all_data['review_answer_timestamp'] - all_data['review_creation_date']
    all_data['product_volume'] = all_data['product_length_cm'] * all_data['product_height_cm'] * all_data['product_width_cm']
    
    return all_data



def convertToDate(all_data, columns):
    """
    Convierte las columnas pasadas en 'columns' a datetime con el formato '%Y-%m-%d %H:%M:%S'
    """
    for col in columns:
            all_data[col] = all_data[col].astype(np.int64)
            
            
def convertToInt64(all_data, columns):
    """
    Convierte las columnas pasadas a 'Int64'
    """
    for col in columns:
            all_data[col] = pd.to_datetime(all_data[col], format='%Y-%m-%d %H:%M:%S')
            
            
def deleteEmptyEntries(all_data, column1, column2):
    """
    Elimina entradas vacías mediante el uso de otras características o el uso de estadísticas (media / mediana)
    """
    missing = all_data[column1] - all_data[column2]
    # tomamos la mediana porque hay quienes aprueban directamente desde el momento en que ordena, algunos son de hasta 60 días
    add = all_data[all_data[column1].isnull()][column2] + missing.median()
    all_data[column1]= all_data[column1].replace(np.nan, add)




