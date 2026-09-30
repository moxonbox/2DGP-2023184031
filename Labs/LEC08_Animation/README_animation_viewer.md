# 스프라이트 애니메이션 뷰어

Python과 설치된 `pico2d`를 사용합니다. 저장소 루트에서 실행합니다.

```powershell
python Labs/LEC08_Animation/animation_viewer.py
```

이미지는 스크립트 위치를 기준으로 읽으므로 다른 작업 폴더나 IDE에서도 실행할 수 있습니다.
창 테두리를 드래그하면 크기가 바뀝니다. ESC 또는 창 닫기로 종료합니다.

## 재생 규칙

같은 폴더의 `SamuraiSheet.png`와 `sonic-sprite.png`를 사용합니다.
사무라이 시트는 128 × 128 격자이고, 소닉 시트는 프레임 위치·너비·높이가 불규칙합니다.

| 동작 | 이미지 | 프레임 수 | 5회 재생 | 정지 |
| --- | --- | --- | --- | --- |
| 걷기 | SamuraiSheet.png | 8 | 4초 | 1초 |
| 뛰기 | SamuraiSheet.png | 8 | 4초 | 1초 |
| 점프 | SamuraiSheet.png | 12 | 6초 | 1초 |
| 공격 | SamuraiSheet.png | 6 | 3초 | 1초 |
| 소닉 회전 점프 | sonic-sprite.png | 9 | 4.5초 | 1초 |
| 소닉 구르기 | sonic-sprite.png | 6 | 3초 | 1초 |
| 소닉 공중 회전 | sonic-sprite.png | 8 | 4초 | 1초 |
| 소닉 승리 | sonic-sprite.png | 2 | 1초 | 1초 |

초당 10프레임으로 재생합니다. 각 동작을 5회 재생한 뒤 마지막 프레임을 1초간 유지하고 다음 동작으로 넘어갑니다.
소닉 승리가 끝나면 걷기부터 다시 시작하며, 전체 순환은 37.5초입니다. 창 제목에 현재 동작과 정지 여부를 표시합니다.

프레임 중심은 항상 창 중심입니다. 각 동작의 최대 프레임 너비·높이를 기준으로 창 너비·높이의 절반 영역에 맞춥니다.
같은 동작에는 동일한 배율을 적용해 불규칙한 프레임 사이에서도 비율과 확대 배율을 유지합니다.
사무라이 정사각형 프레임의 한 변은 기존처럼 `min(창 너비, 창 높이) / 2`이며 투명 여백을 포함합니다.
정지 중에도 창 크기 변경과 종료 입력을 처리합니다.

## 프레임 정보 추가

`animation_viewer.py`의 `ANIMATIONS`에 `(동작 이름, 이미지 파일명, 프레임 튜플)`을 추가합니다.
각 프레임은 이미지 왼쪽 위를 기준으로 `(left, top, width, height)`를 저장합니다.

```python
("소닉 승리", "sonic-sprite.png", (
    (96, 427, 23, 39),
    (125, 427, 23, 39),
)),
```

`frame_rectangle()`이 pico2d의 왼쪽 아래 좌표로 변환합니다.
프레임 수는 `len(frames)`에서 구하므로 별도의 개수 설정이 필요하지 않습니다.
규칙적인 시트는 `grid_frames(행 번호, 프레임 수)`로 좌표를 생성합니다. 행 번호는 위에서부터 0으로 시작합니다.
이미지는 파일별로 한 번만 로딩합니다.

## 검증

```powershell
python Labs/LEC08_Animation/test_animation_viewer.py
python Labs/LEC08_Animation/test_animation_viewer.py --smoke
```

첫 명령은 8종의 서로 다른 프레임 수, 모든 반복 프레임, 정지 시작·종료, 전체 순환, 잘라내기 좌표, 비율·배율 유지와 종료 입력을 검사합니다.
`--smoke`는 실제 pico2d 창을 열어 숨긴 뒤 PNG 2개 로딩, 3가지 창 크기, 모든 프레임의 렌더링과 SDL 종료 이벤트를 추가로 검사합니다.
추가 테스트 라이브러리는 필요하지 않습니다.

참고 자료: `Slides/LEC 08 애니메이션.html`의 프레임 좌표, 순환, 확대 출력 설명.
창 크기 변경은 pico2d가 사용하는 [SDL_SetWindowResizable](https://wiki.libsdl.org/SDL2/SDL_SetWindowResizable)을 사용합니다.
현재 pico2d의 `get_events()`는 크기 변경 이벤트를 생략하므로 `SDL_GetWindowSize()`로 실제 크기를 확인합니다.
