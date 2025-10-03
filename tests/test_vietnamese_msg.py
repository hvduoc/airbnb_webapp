import json
import re

import requests

print("Testing Vietnamese upload message...")

# Prepare data
csv_content = '''Nhà/phòng cho thuê,Check-in,Check-out,Số đêm,Khách,Tình trạng,Thu nhập tổng,Phí dọn dẹp
"Avalon 5.3 - OceanSight - New interior, central",2024-01-01,2024-01-03,2,2,Confirmed,2000000,200000'''

room_mapping = {'mappings': {'Avalon 5.3 - OceanSight - New interior, central': 'AVA-503'}}

files = {'files': ('reservations.csv', csv_content, 'text/csv')}
data = {'room_mapping': json.dumps(room_mapping)}

try:
    # Test upload
    response = requests.post('http://127.0.0.1:8009/upload', files=files, data=data, timeout=30)
    
    html = response.text
    
    # Check for Vietnamese messages
    vietnamese_indicators = [
        'Tải lên thành công',
        'Thống kê:',
        'bản ghi mới',
        'bản ghi cập nhật',
        'Thời gian xử lý'
    ]
    
    found_vietnamese = []
    for indicator in vietnamese_indicators:
        if indicator in html:
            found_vietnamese.append(indicator)
    
    if found_vietnamese:
        print(f"✅ Found Vietnamese elements: {found_vietnamese}")
        
        # Try to extract message content
        msg_patterns = [
            r'<div[^>]*white-space:\s*pre-line[^>]*>([^<]*)</div>',
            r'<div[^>]*>([^<]*Tải lên thành công[^<]*)</div>',
            r'<p[^>]*>([^<]*bản ghi[^<]*)</p>'
        ]
        
        for pattern in msg_patterns:
            matches = re.findall(pattern, html, re.DOTALL | re.IGNORECASE)
            if matches:
                print(f"📊 Message found: {matches[0].strip()}")
                break
    else:
        print("❌ No Vietnamese upload message found")
        if 'Files processed successfully' in html:
            print("Found English message instead")
        
        # Show a snippet around upload result area
        if '<div class="card"' in html:
            start = html.find('<div class="card"')
            end = html.find('</div>', start) + 6
            print(f"Card content preview: {html[start:end]}")
            
except Exception as e:
    print(f"❌ Test failed: {e}")