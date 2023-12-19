import json
import asyncio
import uvicorn
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.requests import Request
import mysql.connector

app = Starlette(debug=True)

async def handle_post_request(request: Request) -> JSONResponse:
    data = await request.json()
    number = int(data.get("number"))
    response = await process_request(number)
    return JSONResponse(response)

async def process_request(number: int) -> dict:
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="nikitin",
            password="nikitin",
            database="test"
        )
        cursor = connection.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS numbers (processed_number INT)")
        cursor.execute("SELECT * FROM numbers WHERE processed_number = %s", (number,))
        result = cursor.fetchone()
        if result is not None:
            raise ValueError("Полученное число равно обработанному числу")
        cursor.execute("SELECT * FROM numbers WHERE processed_number = %s", (number+1,))
        result = cursor.fetchone()
        if result is not None:
            raise ValueError("Полученное число меньше на единицу уже обработанного числа")
        cursor.execute("INSERT INTO numbers (processed_number) VALUES (%s)", (number,))
        connection.commit()
        response = {"result": number + 1}
        cursor.close()
        connection.close()
        return response
    except (mysql.connector.Error, ValueError) as e:
        return {"error": str(e)}

app.add_route("/", handle_post_request, methods=["POST"])

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=6000)
