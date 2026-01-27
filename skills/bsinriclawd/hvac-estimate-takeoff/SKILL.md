name: hvac_estimate_takeoff
description: HVAC takeoff from PDF plans (equipment counts and schedules)
trigger: file_upload
file_types: [pdf]
tools:
  - pymupdf-pdf
output: table
