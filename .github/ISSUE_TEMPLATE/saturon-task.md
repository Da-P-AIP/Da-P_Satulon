---
name: Saturon Task
about: G1–G5 フェーズ別タスクやバグ報告用テンプレ
title: ''
labels: ''
assignees: ''

---

name: "Saturon Task"
description: G1–G5 各フェーズのタスク／バグを登録
title: "[PHASE]: <短い概要>"
labels:
  - topic:information_conductivity
body:
  - type: dropdown
    id: phase
    attributes:
      label: "Phase"
      options:
        - G1
        - G2
        - G3
        - G4
        - G5
      description: "該当フェーズを選択"
  - type: textarea
    id: breakdown
    attributes:
      label: "Task Breakdown"
      description: "やることを箇条書きで"
      placeholder: "- [ ] サブタスクA\n- [ ] サブタスクB"
    validations:
      required: true
