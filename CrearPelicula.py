import boto3
import uuid
import os
import json
import traceback


def imprimir_log(tipo_log, datos_del_log):
    # Log json estándar en CloudWatch:
    # { "tipo": "INFO" / "ERROR", "log_datos": { ... } }
    log_estandar = {
        "tipo": tipo_log,
        "log_datos": datos_del_log
    }
    # json.dumps genera json válido (comillas dobles) para que Logs Insights
    # detecte automáticamente los campos tipo, log_datos.*, etc.
    print(json.dumps(log_estandar, ensure_ascii=False, default=str))


def lambda_handler(event, context):
    try:
        # Entrada (json)
        tenant_id = event['body']['tenant_id']
        pelicula_datos = event['body']['pelicula_datos']
        nombre_tabla = os.environ["TABLE_NAME"]

        # Proceso
        uuidv4 = str(uuid.uuid4())
        pelicula = {
            'tenant_id': tenant_id,
            'uuid': uuidv4,
            'pelicula_datos': pelicula_datos
        }
        dynamodb = boto3.resource('dynamodb')
        tabla = dynamodb.Table(nombre_tabla)
        respuesta_dynamodb = tabla.put_item(Item=pelicula)

        # Salida (json) - Log INFO en CloudWatch
        imprimir_log("INFO", pelicula)

        return {
            'statusCode': 200,
            'pelicula': pelicula,
            'response': respuesta_dynamodb
        }

    except Exception as error:
        # Salida (json) - Log ERROR en CloudWatch
        datos_del_error = {
            "tipo_error": type(error).__name__,
            "mensaje_error": str(error),
            "detalle_error": traceback.format_exc(),
            "evento_recibido": event
        }
        imprimir_log("ERROR", datos_del_error)

        return {
            'statusCode': 500,
            'error': {
                'tipo_error': type(error).__name__,
                'mensaje_error': str(error)
            }
        }
