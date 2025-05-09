import os
from typing import List, Optional
import requests
from fastapi import FastAPI, UploadFile, Form, HTTPException
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()

# ----- OpenAPI Metadata -----
app = FastAPI(
    title="ECOLOGIC Middleware API",
    description="""
    This API serves as a middleware for integrating data from:
    
        • Sensors (IoT devices)
        • Autodesk Revit BIM systems
        • SAP ERP systems

    A Middleware Component solution for construction site management,
    demonstrating interoperability between systems using REST APIs.
    """,
    version="1.0.0",
)

sensor_store: dict[str, dict] = {}

# SAP
SAP_API_KEY = os.getenv("SAP_API_KEY")
SAP_API_BASE = os.getenv("SAP_API_BASE")

# --- Sensor Endpoints ---
class SensorData(BaseModel):
    sensor_id: str = Field(..., title="Sensor ID", description="The unique identifier for the sensor.")
    value: float = Field(..., title="Sensor Value", description="The measurement value from the sensor.")
    timestamp: str = Field(..., title="Timestamp", description="ISO 8601 date/time of the measurement.")

@app.post("/sensor-data", tags=["Sensors"])
async def receive_sensor_data(sensor: SensorData):
    sensor_store[sensor.sensor_id] = sensor.dict()
    return {"message": "Sensor data received", **sensor.dict()}

@app.get("/sensor-data/{sensor_id}", tags=["Sensors"])
async def get_sensor_data(sensor_id: str):
    data = sensor_store.get(sensor_id)
    if not data:
        raise HTTPException(404, "Sensor with the specified ID not found")
    return {**data, "unit": "°C"}

# --- BIM Integration (Autodesk Revit) ---
class BIMUpdate(BaseModel):
    status: str = Field(..., title="BIM Object Status", description="New status (e.g., 'Installed').")

@app.get("/bim/{object_id}", tags=["BIM (Autodesk Revit)"])
async def get_bim_object(object_id: str):
    return {
        "object_id": object_id,
        "type": "Door",
        "dimensions": {"height": "2.1m", "width": "0.9m"},
        "status": "Installed",
        "location": {"floor": "1st", "room": "101"},
    }

@app.put("/bim/{object_id}", tags=["BIM (Autodesk Revit)"])
async def update_bim_object(object_id: str, update: BIMUpdate):
    return {"message": f"BIM object {object_id} updated successfully", "new_status": update.status}

# --- ERP Integration (SAP) ---
class WorkOrder(BaseModel):
    work_order_id: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)
    cost_center: str = Field(..., min_length=1)
    due_date: str 

@app.get("/erp/material/{material_id}", tags=["ERP (SAP)"])
async def get_material_info(material_id: str):
    return {
        "material_id": material_id,
        "description": "Concrete",
        "stock": 200,
        "unit": "cubic meters",
        "plant": "Plant_001",
    }

@app.post("/erp/work-order", status_code=201, tags=["ERP (SAP)"])
async def create_work_order(work_order: WorkOrder):
    return {
        "message": f"Work Order {work_order.work_order_id} created in SAP",
        "description": work_order.description,
        "cost_center": work_order.cost_center,
        "due_date": work_order.due_date,
    }

# --- SAP Endpoint, simplified output ---
@app.get("/erp/serial-numbers", tags=["ERP (SAP)"])
async def get_material_serial_numbers(
    top: int = 50,
    skip: int = 0,
    filter: Optional[str] = None
):
    if not SAP_API_KEY or not SAP_API_BASE:
        raise HTTPException(500, "SAP_API_KEY or SAP_API_BASE not configured")

    url = f"{SAP_API_BASE}/A_MaterialSerialNumber"
    params = {"$top": top, "$skip": skip, "$inlinecount": "allpages"}
    if filter:
        params["$filter"] = filter

    headers = {"APIKey": SAP_API_KEY, "Accept": "application/json"}
    resp = requests.get(url, headers=headers, params=params)
    if not resp.ok:
        raise HTTPException(status_code=resp.status_code, detail=resp.text)

    payload = resp.json().get("d", {})
    raw_items = payload.get("results", [])
    simplified_items = [
        {
            "material": i.get("Material"),
            "serial": i.get("SerialNumber"),
            "plant": i.get("Plant"),
            "location": i.get("StorageLocation"),
            "batch": i.get("Batch") or None,
            "equipment_id": i.get("Equipment") or None
        }
        for i in raw_items
    ]

    return {
        "total_count": int(payload.get("__count", 0)),
        "items": simplified_items
    }

# --- File Upload / Notification Endpoints ---
@app.post("/upload/manual-data", tags=["Manual Processes"])
async def upload_manual_data(file: UploadFile):
    content = await file.read()
    return {"filename": file.filename, "content_size": len(content)}

@app.post("/notifications", tags=["Manual Processes"])
async def send_notification(email: str = Form(...), message: str = Form(...)):
    return {"message": f"Notification sent to {email}", "content": message}

# --- Machine Learning ---
@app.post("/ml/predict-equipment-failure", tags=["Machine Learning"])
async def predict_equipment_failure(sensor_data: List[SensorData]):
    return {"prediction": "High probability of failure", "failure_probability": 0.85}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)