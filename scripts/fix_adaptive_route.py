from pathlib import Path

app = Path('app.js')
text = app.read_text(encoding='utf-8')

old_add = "function addLevel(level){if(!state.visitedLevels.includes(level))state.visitedLevels.push(level);state.queue.push(...sampleLevel(level));renderRoute()}"
new_add = "function addLevel(level){if(!state.visitedLevels.includes(level))state.visitedLevels.push(level);state.queue.push(...sampleLevel(level));if(['cs','de'].includes(state.candidate?.language)){const speakingPool=state