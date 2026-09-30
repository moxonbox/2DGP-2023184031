# 스프라이트 애니메이션 뷰어

Python과 설치된 `pico2d`를 사용합니다. 저장소 루트에서 실행합니다.

```powershell
python Labs/LEC08_Animation/animation_viewer.py
```

이미지는 스크립트 위치를 기준으로 읽으므로 다른 작업 폴더나 IDE에서도 실행할 수 있습니다.
창 테두리를 드래그하면 크기가 바뀝니다. ESC 또는 창 닫기로 종료합니다.

## 재생 규칙

같은 폴더의 `SamuraiSheet.png`에서 128 × 128 프레임을 잘라 사용합니다.
행 번호는 위에서부터 0으로 시작합니다.

| 동작 | 행 | 프레임 수 | 5회 재생 | 정지 |
| --- | --- | --- | --- | --- |
| 걷기 | 1 | 8 | 4초 | 1초 |
| 뛰기 | 2 | 8 | 4초 | 1초 |
| 점프 | 3 | 12 | 6초 | 1초 |
| 공격 | 4 | 6 | 3초 | 1초 |

초당 10프레임으로 재생합니다. 각 동작을 5회 재생한 뒤 마지막 프레임을 1초간 유지하고 다음 동작으로 넘어갑니다.
공격이 끝나면 걷기부터 다시 시작하며, 전체 순환은 21초입니다. 창 제목에 현재 동작과 정지 여부를 표시합니다.

프레임 중심은 항상 창 중심입니다. 정사각형 프레임의 한 변은 `min(창 너비, 창 높이) / 2`입니다.
창 절반 영역 안에 원본 비율을 유지하며 배치합니다. PNG의 투명 여백도 프레임 크기에 포함됩니다.
정지 중에도 창 크기 변경과 종료 입력을 처리합니다.

## 검증

```powershell
python Labs/LEC08_Animation/test_animation_viewer.py
python Labs/LEC08_Animation/test_animation_viewer.py --smoke
```

첫 명령은 모든 반복 프레임, 정지 시작·종료, 전체 순환, 출력 좌표, 종료 입력을 검사합니다.
`--smoke`는 실제 pico2d 창을 열어 숨긴 뒤 PNG 로딩, 3가지 창 크기, 모든 프레임의 렌더링과 SDL 종료 이벤트를 추가로 검사합니다.
추가 테스트 라이브러리는 필요하지 않습니다.

참고 자료: `Slides/LEC 08 애니메이션.html`의 프레임 좌표, 순환, 확대 출력 설명.
창 크기 변경은 pico2d가 사용하는 [SDL_SetWindowResizable](https://wiki.libsdl.org/SDL2/SDL_SetWindowResizable)을 사용합니다.
현재 pico2d의 `get_events()`는 크기 변경 이벤트를 생략하므로 `SDL_GetWindowSize()`로 실제 크기를 확인합니다.
