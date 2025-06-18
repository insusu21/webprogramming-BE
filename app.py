from flask import Flask, request, jsonify
from flask import session
from pymongo import MongoClient
import bcrypt
from flask_cors import CORS
from flask_login import LoginManager
from flask_login import UserMixin
from flask_login import login_user
from flask_restx import Api, Resource
from datetime import timedelta

app = Flask(__name__)
app.secret_key = 'ase123e2d2nn2l12n3'
app.config['SESSION_PERMANENT'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=1)
app.config['SESSION_COOKIE_SAMESITE'] = 'None'
app.config['SESSION_COOKIE_SECURE'] = True 
CORS(app, supports_credentials=True, origins=["http://localhost:8080"])


#세션
login_manager = LoginManager()
login_manager.init_app(app)
@login_manager.user_loader
def load_user(user_id):
    # user_id로 DB에서 사용자 조회 후 User 객체 반환
    user_data = user_col.find_one({"_id": ObjectId(user_id)})
    if user_data:
        return User(str(user_data['_id']), user_data['email'], user_data['name'])
    return None

class User(UserMixin):
    def __init__(self, id, email, name):
        self.id = id
        self.email = email
        self.name = name

    def get_id(self):
        return self.id

# Swagger 설정
api = Api(app, version='1.0', title='Travel API',
          description='A simple API for travel destinations and reviews')

# 리소스 정의: API 엔드포인트에 해당
ns = api.namespace('Reviews', description='Operations related to reviews')

# MongoDB 연결
client = MongoClient("mongodb://localhost:27017/")
db = client["trabledb"]
user_col = db["users"]
dest_col = db["destinations"]  # 여행지 정보를 위한 컬렉션
review_col = db["reviews"]  # 리뷰 정보를 위한 컬렉션

initial_destinations = [
    {"name": "경복궁", "description": "한국의 대표적인 전통 궁궐", "type": "문화, 도시", "imageUrl": "https://search.pstatic.net/common/?src=http%3A%2F%2Fcafefiles.naver.net%2F20101110_89%2Fyoon1000510_12894008089823VwBE_jpg%2F11%252C10_%25B0%25E6%25C8%25B8%25B7%25E7-03_yoon1000510.jpg&type=a340"},
    {"name": "제주도", "description": "자연과 바다가 아름다운 섬", "type": "섬, 인기, 해변, 자연" , "imageUrl": "https://search.pstatic.net/common/?src=http%3A%2F%2Fblogfiles.naver.net%2FMjAxNzA2MDhfMTMx%2FMDAxNDk2ODg0MDk1Mjcw.nyRzE4I-fUjFntHS6CYUfn9GWq1NCxMa5NaZ_-CvEs8g.X1AGx19FIeR8SyeIlGQNjZo2sGQVCGJOo3GM99XbipIg.JPEG.shj7107%2F6.jpg&type=sc960_832"},
    {"name": "부산 해운대", "description": "한국에서 가장 유명한 해변 중 하나", "type": "인기, 해변" , "imageUrl": "https://search.pstatic.net/common/?src=http%3A%2F%2Fblogfiles.naver.net%2FMjAyNDAyMTJfMjE5%2FMDAxNzA3NzQxOTczNDQ5.zb9jf4B-XOnKtFYx8LStzod2d3l8yjLsay6BVynMlWcg.T_ol8-E-VoO8a5IIdxCCeJibAmxRjiPT-O6IbitwSlAg.JPEG.bisr2da%2F1707741972438.jpg&type=sc960_832"},
    {"name": "남산타워", "description": "서울 전망을 볼 수 있는 타워", "type": "인기, 자연" , "imageUrl": "https://search.pstatic.net/common/?src=http%3A%2F%2Fblogfiles.naver.net%2F20150807_215%2Fchjfine_1438952708737R2XKj_JPEG%2F1438941154054.jpeg&type=sc960_832"},
    {"name": "부산 광안리", "description": "야경이 멋진 부산의 해변", "type": "인기, 해변" , "imageUrl": "https://search.pstatic.net/common/?src=http%3A%2F%2Fblogfiles.naver.net%2FMjAyNTAyMDNfMjI3%2FMDAxNzM4NTYyNzE0MTEy.Yj_yobVbybOg4PCpwygjR1M6DcarMT1s3v-HOWONr6Ag._4o7j2-zGNdbOF9aCXcTQySBziNFbraSdVdIS4q-OEUg.JPEG%2F900%25A3%25DF20250203%25A3%25DF141900%25A3%25DF953.jpg&type=a340"},
    {"name": "속초", "description": "동해와 산의 조화", "type": "인기, 도시, 해변" , "imageUrl": "https://search.pstatic.net/common/?src=http%3A%2F%2Fblogfiles.naver.net%2FMjAyMzExMDZfODEg%2FMDAxNjk5MjcyMjU1ODAz.NehVTLdRDe78xfezPL4P2a4n133QPop6mEi_ebJVoNEg.xL0daf-j9XukQ4j0SZcIOXBLBccMBjqK0IAHNG2Exc8g.JPEG.cgnara%2F20231106%25A3%25DF182227.jpg&type=a340"},
    {"name": "강릉", "description": "바다와 커피 거리로 유명한 도시", "type": "인기, 도시", "imageUrl": "https://search.pstatic.net/common/?src=http%3A%2F%2Fimgnews.naver.net%2Fimage%2F001%2F2023%2F05%2F02%2FPYH2023050211010006200_P4_20230502133914104.jpg&type=a340"},
    {"name": "경주", "description": "역사적인 유적이 많은 도시", "type": "인기, 도시", "imageUrl": "https://search.pstatic.net/common/?src=http%3A%2F%2Fblogfiles.naver.net%2FMjAyMzA4MTZfNzIg%2FMDAxNjkyMTQ3NjY1MjQ5.yRlPtHyRK0d78WqzgqDDMXtledrDmi3NoCpH1h5131kg.KbHmISUwef_XhqGjKox40NTNebzaqYLwYe-4Zp45_xcg.JPEG.rlwnghks1477%2FKakaoTalk_20230815_212029639_08.jpg&type=a340"},
    {"name": "전주한옥마을", "description": "전통과 현대가 공존하는 공간", "type": "인기, 문화", "imageUrl": "https://search.pstatic.net/common/?src=http%3A%2F%2Fblogfiles.naver.net%2FMjAyMjAxMTlfMjA0%2FMDAxNjQyNTc0MzM1NDY3.uerdQ1VIp1jumb-bCPt2ClX8Y9JXKVRxz5L3lLdhqeUg.byHow7psgNnW7aBNquo5GLIXSkaoSakn2etgpaTqiGog.JPEG.dasanpartner%2FKakaoTalk_20220119_152201377_01.jpg&type=sc960_832"},
    {"name": "담양", "description": "죽녹원으로 유명한 대나무숲", "type": "자연", "imageUrl": "https://search.pstatic.net/common/?src=http%3A%2F%2Fblogfiles.naver.net%2FMjAyMTA2MjhfNzgg%2FMDAxNjI0ODgxMjQyMzc1.aCJ2KG9sKp42leaUCN-GymJBzprWPW23NI-oLpQtOIog.i9Ar-PhZTrlmhR8M7nN5RfzZR71S2a0_0hPDNNN5u5og.JPEG.soock7010%2F1624881243558.jpg&type=sc960_832"},
    {"name": "춘천 남이섬", "description": "데이트 명소로 유명한 섬", "type": "인기, 섬, 자연, 문화", "imageUrl": "https://search.pstatic.net/common/?src=http%3A%2F%2Fimgnews.naver.net%2Fimage%2F5486%2F2022%2F11%2F15%2F0000229999_004_20221115225804073.jpg&type=sc960_832"},
    {"name": "여수", "description": "밤바다와 케이블카로 유명", "type": "인기, 도시, 해변", "imageUrl": "https://search.pstatic.net/common/?src=http%3A%2F%2Fblogfiles.naver.net%2FMjAyMTA2MTVfMjI0%2FMDAxNjIzNzQzOTc3MTc2.OUqQt4L8VnRSwJfGyhXzO5sGsmvp5SSJPaDkzYMU3Bsg.VC6Kg05SAclK3JgWHy37tzs3i2FsvqdVVlKeEf3u_W4g.JPEG.vudod1%2F16236341582751.jpg&type=sc960_832"},
    {"name": "인사동", "description": "전통 공예와 갤러리의 거리", "type": "도시, 문화", "imageUrl": "https://search.pstatic.net/sunny/?src=https%3A%2F%2Fmediahub.seoul.go.kr%2Fwp-content%2Fuploads%2Feditor%2Fimages%2F000559%2F%25EC%259D%25B8%25EC%2582%25AC%25EB%258F%2599_%25EA%25B3%25A8%25EB%25AA%25A9_DSC03586_1.jpg&type=sc960_832"},
    {"name": "서촌", "description": "한적한 골목 문화거리", "type": "도시, 문화", "imageUrl": "https://search.pstatic.net/common/?src=http%3A%2F%2Fblogfiles.naver.net%2FMjAyMjAzMzBfMjA2%2FMDAxNjQ4NjM3MTk0Njcx.zldaVDM5GVY-A01EaFkACE1DgkNgchF-Vzus9X70s-0g.7ht1c2yQtqv_Nikx-3bREKnn8ZaWxJLJ5Z-j5eWD7Vgg.JPEG.subunr7%2F000023.JPG&type=sc960_832"},
    {"name": "하동", "description": "녹차밭과 자연풍경", "type": "자연", "imageUrl": "https://search.pstatic.net/common/?src=http%3A%2F%2Fblogfiles.naver.net%2FMjAyMjA3MjlfNDQg%2FMDAxNjU5MDkxNDQ4NTky.34btOHsTEHGNRhjr4H8QM0Rtr7tODX1H8NGZaCKLBn0g.Ee8F0-IUVAf9y2rVJ2TxWsBSyl0i42-sScecOPsoazcg.JPEG.xodnaka1%2F10%252C4.jpg&type=sc960_832"},
    {"name": "울릉도", "description": "자연이 살아있는 섬", "type": "섬, 자연", "imageUrl": "https://search.pstatic.net/common/?src=http%3A%2F%2Fcafefiles.naver.net%2F20160321_72%2Fbus2897_14585287711298z4Or_JPEG%2F20160321_112043.jpg&type=sc960_832"},
    {"name": "대구 근대골목", "description": "역사 문화 체험 골목", "type": "도시, 문화", "imageUrl": "https://search.pstatic.net/common/?src=http%3A%2F%2Fblogfiles.naver.net%2FMjAyMjAzMjNfMTk3%2FMDAxNjQ4MDMzNTEyNDU3.-gb4VCjP-oae34E_z88Dl7VNe7xzaxKLwrdgC-c11vQg.z0Fu6vtKjtsVkNtvQqvlcKHtbV8l0fZ8fX2kz1YhWg0g.JPEG.minstory98%2FKakaoTalk_20220323_190130141_22.jpg&type=sc960_832"},
    {"name": "통영", "description": "예쁜 바닷가 마을", "type": "해변", "imageUrl": "https://search.pstatic.net/common/?src=http%3A%2F%2Fblogfiles.naver.net%2FMjAxOTAzMDJfODQg%2FMDAxNTUxNDc4NTk5MDcy.h8dkj_Ipc0h7Y7C1CHZVXJmoA2grFlXnK9TKbfzG424g.YEYmrk8U2XcuQ9d0zyKMJzFi8yTyHlTvK95ZwpgVqo0g.JPEG.teramogi%2F15.jpg&type=sc960_832"},
    {"name": "포항 호미곶", "description": "해돋이 명소", "type": "해변", "imageUrl": "https://search.pstatic.net/common/?src=http%3A%2F%2Fblogfiles.naver.net%2FMjAxOTAxMjJfMjQg%2FMDAxNTQ4MDk5ODM0OTg5.m6aR7ojFobDYdTbc4kF2lBj2H9QWZ1vhEIm5JPYkqysg.n_TrtEJrjjaQb0jTgc1m4fg8rN892pljszHWZnHNlSgg.JPEG.kim60644%2F20190117_0032g.JPG&type=sc960_832"},
    {"name": "양양 서피비치", "description": "서핑하기 좋은 해변", "type": "인기, 해변", "imageUrl": "https://search.pstatic.net/common/?src=http%3A%2F%2Fblogfiles.naver.net%2FMjAyMTExMTBfMTg2%2FMDAxNjM2NTQ5OTE1OTM5.MqTw-N2X6bYDvvt7BEE7Yu61ABAdqILzIj1GGLPLK58g.Pn_RuzxiCGy1guyKyx83r2s_s2rnr6yHQK69ppkWf7gg.JPEG.ssoing_jh%2FKakaoTalk_20211110_220713569_05.jpg&type=sc960_832"}
]
dest_col.delete_many({})  # 기존 데이터 제거 (원하면)
dest_col.insert_many(initial_destinations)
############

@app.route('/', methods=['POST']) # 홈페이지 방문
def init_destinations():
    dest_col.delete_many({})  # 기존 데이터 제거 (원하면)
    dest_col.insert_many(initial_destinations)
    return jsonify({"message": "20개 여행지 초기화 완료"}), 201


############################################################################### user관련 
# 회원가입
@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    name = data.get('name')
    phone = data.get('phone')

    # 필수 입력 확인
    if not all([email, password, name, phone]):
        return jsonify({'message': '모든 필드를 입력해주세요.'}), 400

    # 중복 체크
    if user_col.find_one({"email": email}):
        return jsonify({'message': '이미 존재하는 이메일입니다.'}), 409

    # 비밀번호 해싱
    hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    # DB 저장
    user_col.insert_one({
        "email": email,
        "password": hashed_pw,
        "name": name,
        "phone": phone
    })

    return jsonify({'message': '회원가입 성공'}), 201

# 로그인
@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    user_data = user_col.find_one({"email": email})
    if user_data and bcrypt.checkpw(password.encode('utf-8'), user_data['password']):
        user = User(str(user_data['_id']), user_data['email'], user_data['name'])
        login_user(user)  # 세션에 로그인 정보 저장
        session['user_id'] = str(user_data['_id'])
        session.permanent = True
        return jsonify({'message': '로그인 성공', 'user': {
            "id": str(user_data['_id']),
            "email": user_data['email'],
            "name": user_data['name']
        }}), 200
    return jsonify({'message': '로그인 실패'}), 401

from bson.objectid import ObjectId  # ObjectId를 사용하여 _id로 찾기

#로그인 복원
@app.route('/api/me', methods=['GET'])
def get_current_user():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'message': '로그인 필요', 'logged_in': False}), 401
    # DB에서 사용자 정보 조회
    user_data = user_col.find_one({'_id': ObjectId(user_id)})
    if not user_data:
        return jsonify({'message': '사용자 없음', 'logged_in': False}), 401
    return jsonify({
        'id': str(user_data['_id']),
        'email': user_data['email'],
        'name': user_data['name'],
        'logged_in': True
    }), 200

# 회원 정보 수정
@app.route('/api/user/update', methods=['PUT'])
def update_user():
    data = request.json
    user_id = data.get('user_id')  # 유저의 고유 _id
    new_email = data.get('email')  # 이메일 수정 가능하도록 추가
    new_password = data.get('password')
    new_name = data.get('name')
    new_phone = data.get('phone')

    # 필수 입력 확인
    if not all([user_id, new_password, new_name, new_phone]):
        return jsonify({'message': '모든 필드를 입력해주세요.'}), 400

    # 사용자 조회 (_id로 찾기)
    user_data = user_col.find_one({"_id": ObjectId(user_id)})
    if not user_data:
        return jsonify({'message': '사용자를 찾을 수 없습니다.'}), 404
    
    # 중복 체크
    if user_col.find_one({"email": new_email}):
        return jsonify({'message': '이미 존재하는 이메일입니다.'}), 409

    # 비밀번호 해싱
    hashed_pw = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())

    # 업데이트할 데이터 (이메일도 수정 가능하게 추가)
    updated_data = {
        "email": new_email,
        "password": hashed_pw,
        "name": new_name,
        "phone": new_phone
    }

    # 사용자 정보 업데이트
    user_col.update_one({"_id": ObjectId(user_id)}, {"$set": updated_data})

    return jsonify({'message': '회원정보가 수정되었습니다.'}), 200

# 회원 탈퇴
@app.route('/api/user/delete', methods=['DELETE'])
def delete_user():
    data = request.json
    user_id = data.get('user_id')  # 탈퇴하려는 사용자의 _id

    # 필수 입력 확인
    if not user_id:
        return jsonify({'message': '사용자의 고유 ID를 입력해주세요.'}), 400

    # 사용자 조회 (_id로 찾기)
    user_data = user_col.find_one({"_id": ObjectId(user_id)})
    if not user_data:
        return jsonify({'message': '사용자를 찾을 수 없습니다.'}), 404

    # 사용자 정보 삭제
    user_col.delete_one({"_id": ObjectId(user_id)})

    return jsonify({'message': '회원 탈퇴가 완료되었습니다.'}), 200




################################################################################# 여행지 관련

# 여행지 추가
@app.route('/api/destinations/create', methods=['POST'])
def create_destination():
    data = request.json
    name = data.get('name')           # 여행지 이름
    description = data.get('description')  # 여행지 설명

    # 필수 입력 확인
    if not name or not description:
        return jsonify({'message': '여행지 이름과 설명을 입력해주세요.'}), 400

    # 여행지 정보 DB 저장
    dest_col.insert_one({
        "name": name,
        "description": description
    })

    return jsonify({'message': '여행지 정보가 추가되었습니다.'}), 201

# 여행지 정보 수정
@app.route('/api/destinations/update/<string:dest_id>', methods=['PUT'])
def update_destination(dest_id):
    data = request.json
    new_name = data.get('name')           # 수정할 여행지 이름
    new_description = data.get('description')  # 수정할 여행지 설명

    # 필수 입력 확인
    if not new_name or not new_description:
        return jsonify({'message': '여행지 이름과 설명을 입력해주세요.'}), 400

    # 여행지 정보 수정
    #dest_col = db["destinations"]
    result = dest_col.update_one(
        {"_id": ObjectId(dest_id)},  # 여행지의 _id로 찾기
        {"$set": {"name": new_name, "description": new_description}}  # 업데이트할 필드
    )

    if result.matched_count == 0:
        return jsonify({'message': '여행지를 찾을 수 없습니다.'}), 404

    return jsonify({'message': '여행지 정보가 수정되었습니다.'}), 200

# 여행지 삭제
@app.route('/api/destinations/delete/<string:dest_id>', methods=['DELETE'])
def delete_destination(dest_id):
    # 여행지 삭제
    dest_col = db["destinations"]
    result = dest_col.delete_one({"_id": ObjectId(dest_id)})  # _id로 여행지 삭제

    if result.deleted_count == 0:
        return jsonify({'message': '여행지를 찾을 수 없습니다.'}), 404

    return jsonify({'message': '여행지 정보가 삭제되었습니다.'}), 200

# 여행지 목록 조회
@app.route('/api/destinations/list', methods=['GET'])
def get_destinations():
    # 여행지 목록 가져오기
    dest_col = db["destinations"]
    destinations = list(dest_col.find())  # 모든 여행지 데이터를 리스트로 변환

    # ObjectId를 문자열로 변환
    for dest in destinations:
        dest['_id'] = str(dest['_id'])

    return jsonify(destinations), 200

# 여행지 상세 조회
@app.route('/api/destinations/<string:dest_id>', methods=['GET'])
def get_destination(dest_id):
    # 여행지 정보 조회 (_id로 찾기)
    dest_col = db["destinations"]
    destination = dest_col.find_one({"_id": ObjectId(dest_id)})  # _id로 여행지 찾기

    if not destination:
        return jsonify({'message': '여행지를 찾을 수 없습니다.'}), 404

    # ObjectId를 문자열로 변환
    destination['_id'] = str(destination['_id'])

    return jsonify(destination), 200

@app.route('/api/destinations', methods=['GET'])
def get_destinations_by_type():
    category = request.args.get('type')  # 예: '인기', '도시', '자연' 등

    if not category:
        return jsonify({'message': '카테고리(type)를 지정해주세요.'}), 400

    # type 필드에 해당 키워드가 포함된 항목만 필터링 (정규표현식 사용)
    matched = list(dest_col.find({"type": {"$regex": category}}))

    for d in matched:
        d['_id'] = str(d['_id'])

    return jsonify(matched), 200



#################################################################################### 리뷰 관련

# 리뷰 생성
@app.route('/api/reviews/create', methods=['POST'])
def create_review():
    data = request.json
    user_id = data.get('user_id')  # 유저 ID
    dest_id = data.get('dest_id')  # 여행지 ID
    content = data.get('content')  # 리뷰 내용

    # 필수 입력 확인
    if not all([user_id, dest_id, content]):
        return jsonify({'message': '유저 ID, 여행지 ID, 내용은 필수 항목입니다.'}), 400

    # 리뷰 데이터 DB에 저장
    review_col.insert_one({
        "user_id": ObjectId(user_id),
        "dest_id": ObjectId(dest_id),
        "content": content
    })

    return jsonify({'message': '리뷰가 성공적으로 작성되었습니다.'}), 201

# 리뷰 수정
@app.route('/api/reviews/<string:review_id>', methods=['PUT'])
def update_review(review_id):
    data = request.json
    new_content = data.get('content')  # 수정할 리뷰 내용

    # 필수 입력 확인
    if not new_content:
        return jsonify({'message': '리뷰 내용을 입력해주세요.'}), 400

    # 리뷰 정보 조회 (_id로 찾기)
    #review_col = db["reviews"]
    review = review_col.find_one({"_id": ObjectId(review_id)})  # _id로 리뷰 찾기

    if not review:
        return jsonify({'message': '리뷰를 찾을 수 없습니다.'}), 404

    # 리뷰 내용 수정
    review_col.update_one(
        {"_id": ObjectId(review_id)},  # _id로 해당 리뷰 찾기
        {"$set": {"content": new_content}}  # 새로운 내용으로 업데이트
    )

    return jsonify({'message': '리뷰가 수정되었습니다.'}), 200

# 특정 리뷰 상세 조회
@app.route('/api/reviews/<string:review_id>', methods=['GET'])
def get_review_by_id(review_id):
    # 리뷰 ID로 리뷰 정보 조회
    review_col = db["reviews"]
    review = review_col.find_one({"_id": ObjectId(review_id)})  # _id로 리뷰 찾기

    if not review:
        return jsonify({'message': '리뷰를 찾을 수 없습니다.'}), 404

    # _id를 문자열로 변환
    review['_id'] = str(review['_id'])
    review['user_id'] = str(review['user_id'])
    review['dest_id'] = str(review['dest_id'])

    return jsonify(review), 200

# 리뷰 삭제
@app.route('/api/reviews/<string:review_id>', methods=['DELETE'])
def delete_review(review_id):
    # 리뷰 정보 삭제
    review_col = db["reviews"]
    result = review_col.delete_one({"_id": ObjectId(review_id)})  # _id로 리뷰 삭제

    if result.deleted_count == 0:
        return jsonify({'message': '리뷰를 찾을 수 없습니다.'}), 404

    return jsonify({'message': '리뷰가 삭제되었습니다.'}), 200

# 여행지별 리뷰 목록 조회 (쿼리 파라미터 방식 추가)
@app.route('/api/reviews', methods=['GET'])
def get_reviews():
    dest_id = request.args.get('dest_id')
    if dest_id:
        reviews = list(review_col.find({"dest_id": ObjectId(dest_id)}))
        for review in reviews:
            review['_id'] = str(review['_id'])
            review['user_id'] = str(review['user_id'])
            review['dest_id'] = str(review['dest_id'])
        return jsonify(reviews), 200
    return jsonify({'message': 'dest_id 쿼리 파라미터가 필요합니다.'}), 400

# 여행지별 리뷰 목록 조회
@app.route('/api/reviews/destination/<string:dest_id>', methods=['GET'])
def get_reviews_by_dest(dest_id):
    # 여행지 ID로 리뷰들 조회
    review_col = db["reviews"]
    reviews = list(review_col.find({"dest_id": ObjectId(dest_id)}))  # 여행지 ID로 필터링

    # 리뷰가 없을 경우
    if not reviews:
        return jsonify({'message': '이 여행지에 대한 리뷰가 없습니다.'}), 404

    # 리뷰 데이터의 _id를 문자열로 변환
    for review in reviews:
        review['_id'] = str(review['_id'])
        review['user_id'] = str(review['user_id'])
        review['dest_id'] = str(review['dest_id'])

    return jsonify(reviews), 200

# 유저가 작성한 리뷰 조회
@app.route('/api/reviews/user/<string:user_id>', methods=['GET'])
def get_reviews_by_user(user_id):
    # 유저 ID로 리뷰들 조회
    review_col = db["reviews"]
    reviews = list(review_col.find({"user_id": ObjectId(user_id)}))  # 유저 ID로 필터링

    # 리뷰가 없을 경우
    if not reviews:
        return jsonify({'message': '이 유저가 작성한 리뷰가 없습니다.'}), 404

    # 리뷰 데이터의 _id, user_id, dest_id를 문자열로 변환
    for review in reviews:
        review['_id'] = str(review['_id'])
        review['user_id'] = str(review['user_id'])
        review['dest_id'] = str(review['dest_id'])

    return jsonify(reviews), 200












if __name__ == '__main__':
    app.run(debug=True)

