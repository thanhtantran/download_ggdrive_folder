from googleapiclient.discovery import build
from google.oauth2 import service_account
import os

def get_folder_name(service, folder_id):
    """Lấy tên thư mục từ FOLDER_ID"""
    try:
        folder = service.files().get(
            fileId=folder_id,
            fields="name"
        ).execute()
        return folder.get('name', f"drive_folder_{folder_id}")  # Mặc định nếu không có tên
    except Exception as e:
        print(f"❌ Lỗi khi lấy tên thư mục: {e}")
        return f"drive_folder_{folder_id}"

def download_folder(service, folder_id, parent_path="."):
    """Tải toàn bộ thư mục và cấu trúc con"""
    # Lấy tên thư mục và tạo đường dẫn
    folder_name = get_folder_name(service, folder_id)
    folder_path = os.path.join(parent_path, folder_name)
    
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f"📁 Đã tạo thư mục: {folder_path}")

    # Lấy danh sách file trong thư mục
    results = service.files().list(
        q=f"'{folder_id}' in parents",
        fields="files(id, name, mimeType)"
    ).execute()
    items = results.get('files', [])

    if not items:
        print("ℹ️ Thư mục trống!")
        return

    print(f"🔍 Tìm thấy {len(items)} mục trong '{folder_name}'")
    for item in items:
        item_name = item['name']
        item_id = item['id']
        
        if item['mimeType'] == 'application/vnd.google-apps.folder':  # Thư mục con
            print(f"📂 Đang xử lý thư mục con: {item_name}")
            download_folder(service, item_id, folder_path)  # Đệ quy
        else:  # File
            file_path = os.path.join(folder_path, item_name)
            print(f"⬇️ Đang tải: {item_name}")
            request = service.files().get_media(fileId=item_id)
            with open(file_path, 'wb') as f:
                f.write(request.execute())
    print(f"✅ Hoàn thành: {folder_path}")

def main():
    try:
        creds = service_account.Credentials.from_service_account_file('credentials.json')
        service = build('drive', 'v3', credentials=creds)
    except Exception as e:
        print(f"❌ Lỗi khởi tạo API: {e}")
        return

    while True:
        print("\n" + "="*50)
        folder_id = input("Nhập FOLDER_ID (hoặc 'q' để thoát): ").strip()
        
        if folder_id.lower() == 'q':
            print("👋 Đã thoát!")
            break
        
        if not folder_id:
            print("⚠️ Vui lòng nhập FOLDER_ID!")
            continue
        
        download_folder(service, folder_id)  # Tải về thư mục hiện hành

if __name__ == "__main__":
    main()