import requests
import json
import io

print('Testing upload endpoint...')

# CSV test data
csv_content = """Nhà/phòng cho thuê,Check-in,Check-out,Số đêm,Khách,Tình trạng,Thu nhập tổng,Phí dọn dẹp
"Avalon 5.3 - OceanSight - New interior, central",2024-01-01,2024-01-03,2,2,Confirmed,2000000,200000
"Avalon 2.4- OceanSight - New interior, central",2024-01-05,2024-01-07,2,2,Confirmed,1800000,200000"""

room_mapping = {
    'mappings': {
        'Avalon 5.3 - OceanSight - New interior, central': 'AVA-503'
    }
}

try:
    # Prepare file and form data
    files = {'files': ('reservations.csv', csv_content, 'text/csv')}
    data = {'room_mapping': json.dumps(room_mapping)}
    
    response = requests.post(
        'http://127.0.0.1:8008/upload',
        files=files,
        data=data,
        timeout=30
    )
    
    print(f'Response status: {response.status_code}')
    print(f'Response headers: {dict(response.headers)}')
    
    if response.status_code == 200:
        print('✅ Upload successful!')
        print('Response preview:')
        print(response.text[:500] + '...' if len(response.text) > 500 else response.text)
    else:
        print(f'❌ Upload failed!')
        print('Error response:')
        print(response.text[:1000])
        
except requests.exceptions.RequestException as e:
    print(f'❌ Connection error: {e}')
except Exception as e:
    print(f'❌ Unexpected error: {e}')
    import traceback
    traceback.print_exc()