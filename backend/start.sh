#!/bin/bash
cd /media/devmon/sdb1-ata-RESCUE09RM22AR12/www/LCicious/backend
source venv/bin/activate
exec uvicorn app.main:app --host 0.0.0.0 --port 8001
