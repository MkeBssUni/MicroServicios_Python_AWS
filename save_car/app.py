import json
import pymysql

# Configuración de la conexión a la base de datos
rds_host = "database-cafe-balu.cziym6ii4nn7.us-east-2.rds.amazonaws.com"
rds_user = "baluroot"
rds_password = "baluroot"
rds_db = "autos_mike"

def lambda_handler(event, __):
    headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, X-Amz-Date, Authorization, X-Api-Key, X-Amz-Security-Token"
    }

    try:
        body = json.loads(event.get('body', '{}'))

        if not 'brand' in body or not 'model' in body or not 'year' in body or not 'color' in body:
            return {
                "statusCode": 400,
                "headers": headers,
                "body": json.dumps({
                    "message": "MISSING_FIELDS",
                }),
            }

        brand = body.get('brand')
        model = body.get('model')
        year = body.get('year')
        color = body.get('color')

        if not brand or not model or not year or not color:
            return {
                "statusCode": 400,
                "headers": headers,
                "body": json.dumps({
                    "message": "MISSING_FIELDS",
                }),
            }

        if not year.isdigit() or int(year) > 2024:
            return {
                "statusCode": 400,
                "headers": headers,
                "body": json.dumps({
                    "message": "INVALID_YEAR",
                }),
            }

        if car_exists(brand, model, year, color):
            return {
                "statusCode": 400,
                "headers": headers,
                "body": json.dumps({
                    "message": "CAR_EXISTS",
                }),
            }

        return save_car(brand, model, year, color, headers)

    except Exception as e:
        return {
            "statusCode": 500,
            "headers": headers,
            "body": json.dumps({
                "message": "INTERNAL_SERVER_ERROR",
                "error": str(e)
            }),
        }

def connect_to_database():
    try:
        connection = pymysql.connect(host=rds_host, user=rds_user, password=rds_password, db=rds_db)
        return connection
    except pymysql.MySQLError as e:
        raise Exception("ERROR CONNECTING TO DATABASE: " + str(e))

def car_exists(brand, model, year, color):
    connection = connect_to_database()
    cursor = connection.cursor()
    cursor.execute("select * from cars where brand = %s and model = %s and year = %s and color = %s;", (brand, model, year, color))
    result = cursor.fetchall()
    return len(result) > 0

def save_car(brand, model, year, color, headers):
    try:
        connection = connect_to_database()
        cursor = connection.cursor()
        cursor.execute("INSERT INTO cars (brand, model, year, color) VALUES (%s, %s, %s, %s)", (brand, model, year, color))
        connection.commit()

        return {
            "statusCode": 200,
            "headers": headers,
            "body": json.dumps({
                "message": "CAR_SAVED",
            }),
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "headers": headers,
            "body": json.dumps({
                "message": "ERROR_SAVING_CAR",
                "error": str(e)
            }),
        }