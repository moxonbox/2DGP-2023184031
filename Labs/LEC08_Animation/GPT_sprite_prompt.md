# GPT Image 스프라이트 생성 기록

생성 방식: 내장 GPT Image (`image_gen`) 도구.
용도: `animation_viewer.py`가 읽는 PNG 스프라이트 시트.
캐릭터: 청록색 로봇 모험가. 같은 캐릭터의 대기·걷기·뛰기·점프·공격·승리 동작.
각 프레임의 실제 경계를 측정해 불규칙한 `(left, top, width, height)` 좌표로 등록합니다.
행마다 프레임 수가 다르며 기존 5회 반복·1초 정지·중앙 배치·창 크기 대응 규칙을 적용합니다.

## 적용 결과

- 파일: `gpt_robot_sheet.png` (1536 × 1024, RGBA PNG).
- 생성된 PNG 원본을 복사해 사용하며 알파 채널을 보존했습니다.
- 실제 동작별 프레임 수: 대기 4, 걷기 6, 뛰기 5, 점프 5, 공격 6, 승리 3. 합계 29.
- 프롬프트에서 뛰기 6프레임을 요청했으나 실제 출력은 5프레임이므로 확인된 5개만 등록했습니다.
- 프레임마다 실측한 좌표와 투명 여백을 사용합니다. 공격 효과도 프레임에 포함했습니다.
- 실제 pico2d 렌더러에서 투명 배경·점프·공격 효과·승리 동작을 확인했습니다.

## 생성 프롬프트

```text
Use case: stylized-concept.
Asset type: production sprite sheet PNG for a Python pico2d animation viewer.
Create a polished 2D game sprite sheet of one original small teal robot adventurer with a warm amber face screen and a short red scarf. Crisp retro game pixel art, strong silhouette, consistent proportions and palette. Side view facing right throughout, except victory can be three-quarter view.
Canvas: landscape 1536 by 1024. Genuinely transparent background with alpha. No painted checkerboard, ground, cast shadows, scenery, text, grid, labels or watermark.
Layout: exactly six clearly separated horizontal animation rows, read left to right. Generous empty transparent gaps of at least 30 pixels between characters and between rows. Every character and attack effect completely inside its own separated frame area. Never touch adjacent frames. Normal standing height about 105 pixels. Same underlying character scale across all frames; crouched/jumping silhouettes differ in width and height. Allow irregular bounding boxes.
Row 1 (top): IDLE, exactly 4 distinct sequential frames, gentle breathing and head tilt, seamless cycle.
Row 2: WALK, exactly 6 distinct sequential frames, complete walking cycle alternating feet and arms, contact/down/passing/up poses.
Row 3: RUN, exactly 6 distinct sequential frames, energetic full running cycle, forward lean, alternating long strides and airborne passing.
Row 4: JUMP, exactly 5 distinct sequential frames: deep crouch, takeoff, rising tucked legs, descending extended legs, landing crouch.
Row 5: ATTACK, exactly 6 distinct sequential frames: preparation, pull arm back, windup, extended energy punch, follow-through, return to stance. Small amber punch arc stays inside frame.
Row 6 (bottom): VICTORY, exactly 3 distinct sequential frames: hands at chest, one raised arm, both raised arms.
Rows with fewer frames use only left side, leaving the right side transparent. Fit all rows with margins, nothing cropped. Use consistent same character identity. Highest priority: clean separated frames, exact row counts, coherent animation, real transparent alpha.
```
