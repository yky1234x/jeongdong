# AI 시사고발 쇼츠 내레이션 성우 (3탄~7탄 공통)

- 엔진: **Supertonic 3** (Supertone, 다국어 오픈소스) — sherpa-onnx 2.0.2로 로컬 실행, 인터넷 TTS·유료 크레딧 사용 없음
- 성우: **sid = 5** (voice.bin 10개 목소리 중 6번째), 평균 음높이 약 154Hz
- 설정: speed 1.05, num_steps 8, extra {"lang":"ko"}
- 후처리(ffmpeg): 앞뒤 무음 제거 → atempo 1.15 → 장면 앞 0.25초·뒤 0.3초 여백 → 전체 loudnorm(I=-16, TP=-1.5), 44.1kHz 모노
- 원고 규칙: 숫자·영문은 한글로 풀어 쓰기(77일→칠십칠 일, AI→에이아이, QR→큐알, 5인→오인). 붙어 읽혀 뜻이 바뀌는 곳은 '|'로 끊기(예: 사대문|안 국민)
- **edge-tts(InJoon 등)·Higgsfield 목소리 아님**

## 설치·사용
```
pip install sherpa-onnx==2.0.2 numpy        # ffmpeg, npm 필요
python3 setup_voice.py                       # npm에서 모델 받아 ./model 복원 (MD5 확인)
python3 narrate.py out.wav "문장"            # 한 문장
python3 narrate.py narr.wav -f script.txt    # 한 줄 = 한 장면
```
reference_3tan.mp3 = 3탄 내레이션 앞 20초 (목소리 비교용)

## 마무리 멘트(공통 END)
요구는 분명합니다. 부당 징계와 해고 철회, 직장 내 괴롭힘 진상조사. 조합원 여러분, 시민 여러분, 누구도 쉽게 말하지 못하는 이 외벽을 함께 지켜봐 주십시오. 큐알을 찍고 공유해 주세요. 오죽하면 에이아이가 고발합니다.
