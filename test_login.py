import urllib.request
import urllib.parse
import json

# まずログインしてJWTトークンを取得
url = "http://localhost:8000/token"
data = urllib.parse.urlencode({
    "username": "admin",
    "password": "admin123!@#"
}).encode('utf-8')

try:
    req = urllib.request.Request(url, data=data, method='POST')
    req.add_header('Content-Type', 'application/x-www-form-urlencoded')

    with urllib.request.urlopen(req) as response:
        print(f"Login Status Code: {response.getcode()}")
        login_response = response.read().decode('utf-8')
        print(f"Login Response: {login_response}")

        # JWTトークンを抽出
        token_data = json.loads(login_response)
        access_token = token_data['access_token']

        # 招待コード作成APIをテスト（JSON形式）
        invite_url = "http://localhost:8000/api/invite/create"
        invite_data = json.dumps({
            "expires_hours": 168  # 1週間
        }).encode('utf-8')

        invite_req = urllib.request.Request(invite_url, data=invite_data, method='POST')
        invite_req.add_header('Content-Type', 'application/json')
        invite_req.add_header('Authorization', f'Bearer {access_token}')

        with urllib.request.urlopen(invite_req) as invite_response:
            print(f"Invite Create Status Code: {invite_response.getcode()}")
            invite_result = invite_response.read().decode('utf-8')
            print(f"Invite Create Response: {invite_result}")

            # 招待コードを抽出して表示
            invite_data = json.loads(invite_result)
            print(f"\n🎉 新しい招待コードが作成されました！")
            print(f"📧 招待コード: {invite_data['invite_code']}")
            print(f"⏰ 有効期限: {invite_data['expires_at']}")
            print(f"👤 作成者: {invite_data['created_by']}")

            # 招待コードをファイルに保存
            with open('new_invite_code.txt', 'w') as f:
                f.write(f"招待コード: {invite_data['invite_code']}\n")
                f.write(f"有効期限: {invite_data['expires_at']}\n")
                f.write(f"作成者: {invite_data['created_by']}\n")
            print(f"💾 招待コードを 'new_invite_code.txt' に保存しました")

except Exception as e:
    print(f"Error: {e}")