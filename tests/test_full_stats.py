import json

import requests

print("Testing with more data for insert/update stats...")

# CSV with 3 records
csv_content = '''Nhà/phòng cho thuê,Check-in,Check-out,Số đêm,Khách,Tình trạng,Thu nhập tổng,Phí dọn dẹp
"Avalon 5.3 - OceanSight - New interior, central",2024-01-01,2024-01-03,2,2,Confirmed,2000000,200000
"Avalon 2.4- OceanSight - New interior, central",2024-01-05,2024-01-07,2,2,Confirmed,1800000,200000  
"Avalon 3.5 - OceanSight - Central & Mountain view",2024-01-10,2024-01-12,2,4,Confirmed,2200000,250000'''

room_mapping = {
    'mappings': {
        'Avalon 5.3 - OceanSight - New interior, central': 'AVA-503',
        'Avalon 3.5 - OceanSight - Central & Mountain view': 'AVA-305'
    }
}

files = {'files': ('reservations.csv', csv_content, 'text/csv')}
data = {'room_mapping': json.dumps(room_mapping)}

try:
    response = requests.post('http://127.0.0.1:8009/upload', files=files, data=data, timeout=30)
    
    if response.status_code == 200:
        html = response.text
        
        # Find Vietnamese success message
        import re
        msg_pattern = r'<div[^>]*white-space:\s*pre-line[^>]*>(.*?)</div>'
        msg_match = re.search(msg_pattern, html, re.DOTALL)
        
        if msg_match:
            message = msg_match.group(1).strip()
            print("📊 Upload Result:")
            print("=" * 50)
            for line in message.split('\n'):
                print(f"  {line}")
            print("=" * 50)
        else:
            print("❌ Could not extract message")
    else:
        print(f"❌ Upload failed with status {response.status_code}")
        
except Exception as e:
    print(f"❌ Error: {e}")