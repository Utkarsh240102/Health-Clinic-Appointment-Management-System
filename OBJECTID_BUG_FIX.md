# ObjectId Type Mismatch Bug Fix

## Problem Summary
Appointments were not showing up in the frontend because of a critical data type mismatch:
- **Symptom**: User booked appointments but they appeared "not found" or empty
- **Root Cause**: `doctorId` and `patientId` were stored as **strings** in appointments collection, but `_id` in users collection were **ObjectIds**
- **Impact**: All appointment-user joins failed, making appointments appear orphaned

## Technical Details

### Issue
When creating appointments, the code was storing:
```python
appointment_doc = {
    "doctorId": doctor_id,  # String: "691de48df882cea9d101bd82"
    "patientId": patient_id,  # String: "691e1374136185ec68581c5b"
    ...
}
```

But when querying users:
```python
user = await users_collection.find_one({'_id': apt['doctorId']})
# ❌ Comparing string "691de..." with ObjectId(691de...)
# Result: None (not found)
```

### Fix Applied

1. **Store as ObjectIds** (app/services/appointment_service.py)
```python
appointment_doc = {
    "doctorId": ObjectId(doctor_id),  # Convert to ObjectId
    "patientId": ObjectId(patient_id),  # Convert to ObjectId
    ...
}
```

2. **Query with ObjectIds**
```python
# In get_appointments()
if role == "doctor":
    query = {"doctorId": ObjectId(user_id)}
else:
    query = {"patientId": ObjectId(user_id)}

# In get_doctor_slots()
booked = await appointments_collection.find({
    "doctorId": ObjectId(doctor_id),
    ...
})

# In get_doctor_stats() aggregation
pipeline = [
    {"$match": {"doctorId": ObjectId(doctor_id)}},
    ...
]
```

3. **Convert back to strings for API responses**
```python
for apt in appointments:
    apt["_id"] = str(apt["_id"])
    apt["doctorId"] = str(apt["doctorId"])  # JSON serialization
    apt["patientId"] = str(apt["patientId"])  # JSON serialization
```

4. **Fix authorization checks**
```python
# Compare as strings since user_id is string from JWT
if str(appointment["patientId"]) != user_id:
    raise HTTPException(...)
```

## Files Modified

### backend/app/services/appointment_service.py
- Line 67-68: Store doctorId/patientId as ObjectIds
- Line 118-120: Query with ObjectIds in get_appointments()
- Line 142-144: Convert to strings for response
- Line 155-157: Convert to strings in get_appointment_by_id()
- Line 187, 193: Fix authorization comparisons
- Line 264: Query with ObjectId in get_doctor_slots()
- Line 315: Query with ObjectId in aggregation
- Line 378: Count with ObjectId in get_doctor_stats()
- Line 82-84: Convert to strings in create_appointment()

### backend/app/routes/appointments.py
- Line 90: Fix authorization check to compare strings

### backend/migrate_appointment_ids.py (NEW)
- Migration script to convert 385 existing appointments from string IDs to ObjectIds
- Result: 385 migrated, 0 skipped, 0 errors

## Migration Results

```
Total appointments: 385
Migrated: 385
Skipped (already ObjectIds): 0
Errors: 0
```

All existing appointments successfully migrated from string IDs to ObjectIds.

## Verification

Before fix:
```
Doctor: Not found
Patient: Not found
```

After fix:
```
Doctor: Dr. Joan Prince
Patient: Utkarsh Gupta
Start: 2025-12-08 15:00:00
Status: scheduled
Reason: Testing
```

## Impact
- ✅ Appointments now correctly associate with doctors and patients
- ✅ Frontend can fetch and display appointments
- ✅ Authorization checks work properly
- ✅ SMS notifications can find doctor/patient info
- ✅ Statistics and aggregations work correctly

## Note
Backend auto-reload should apply changes immediately. If not, restart backend:
```bash
cd backend
.\venv\Scripts\Activate.ps1
uvicorn app.main:app --reload
```

Frontend will automatically show appointments after backend fix is live.
