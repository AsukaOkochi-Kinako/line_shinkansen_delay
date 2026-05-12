/* ========================================
   どうぶつインディアンポーカー - ゲームロジック
   ======================================== */

// ==================== 動物リスト ====================
const ANIMALS = [
  { e: '🐶', n: 'いぬ' },
  { e: '🐱', n: 'ねこ' },
  { e: '🐭', n: 'ねずみ' },
  { e: '🐹', n: 'ハムスター' },
  { e: '🐰', n: 'うさぎ' },
  { e: '🦊', n: 'きつね' },
  { e: '🐻', n: 'くま' },
  { e: '🐼', n: 'パンダ' },
  { e: '🐨', n: 'コアラ' },
  { e: '🐯', n: 'とら' },
  { e: '🦁', n: 'ライオン' },
  { e: '🐮', n: 'うし' },
  { e: '🐷', n: 'ぶた' },
  { e: '🐸', n: 'かえる' },
  { e: '🐵', n: 'さる' },
  { e: '🐔', n: 'にわとり' },
  { e: '🐧', n: 'ペンギン' },
  { e: '🦆', n: 'あひる' },
  { e: '🦉', n: 'ふくろう' },
  { e: '🐺', n: 'おおかみ' },
  { e: '🐴', n: 'うま' },
  { e: '🦄', n: 'ユニコーン' },
  { e: '🐝', n: 'みつばち' },
  { e: '🦋', n: 'ちょうちょ' },
  { e: '🐢', n: 'かめ' },
  { e: '🐬', n: 'イルカ' },
  { e: '🐳', n: 'くじら' },
  { e: '🦈', n: 'さめ' },
  { e: '🐊', n: 'わに' },
  { e: '🦒', n: 'きりん' },
  { e: '🐘', n: 'ぞう' },
  { e: '🦓', n: 'シマウマ' },
  { e: '🐪', n: 'らくだ' },
  { e: '🦘', n: 'カンガルー' },
  { e: '🦔', n: 'ハリネズミ' },
  { e: '🦝', n: 'アライグマ' },
  { e: '🦙', n: 'アルパカ' },
  { e: '🐿️', n: 'リス' },
  { e: '🦅', n: 'わし' },
  { e: '🦜', n: 'オウム' },
];

// ==================== 画面別 背景色 (hex) ====================
// .app の background-color だけ変える → background-image のグリッドは残る
const BG = {
  home:      '#4EC9F5',  // スカイブルー
  rules:     '#4EC9F5',
  setup:     '#4EC9F5',
  turn:      '#FF5BA8',  // ホットピンク
  countdown: '#FFE600',  // イエロー
  animal:    '#4EC9F5',
  guess:     '#FFFFFF',  // ホワイト
  over:      '#4EC9F5',
};

// ==================== ゲーム状態 ====================
let state = {
  count: 0,       // プレイヤー人数
  current: 0,     // 現在のプレイヤーインデックス
  animals: [],    // 各プレイヤーの動物
  scores: [],     // 各プレイヤーの正解数
};

let countdownTimer = null;

// ==================== 画面遷移 ====================
function go(screenKey) {
  document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
  document.getElementById('s-' + screenKey).classList.add('active');

  // 背景色だけ切り替える (background-image のグリッドを維持するため)
  if (BG[screenKey]) {
    document.getElementById('app').style.backgroundColor = BG[screenKey];
  }
}

// ==================== 初期化: 浮かぶ背景動物 ====================
function initBgAnimals() {
  const container = document.getElementById('bg-animals');
  const pool = ['🐶', '🐱', '🐰', '🦊', '🐻', '🐼', '🐨', '🦁', '🐸', '🐵', '🐧', '🦆'];

  for (let i = 0; i < 9; i++) {
    const el = document.createElement('div');
    el.className = 'bg-animal';
    el.textContent = pool[i % pool.length];
    el.style.left = `${Math.random() * 88}%`;
    el.style.fontSize = `${2.2 + Math.random() * 2}rem`;
    el.style.animationDuration = `${9 + Math.random() * 11}s`;
    el.style.animationDelay = `${-Math.random() * 16}s`;
    container.appendChild(el);
  }
}

// ==================== ルール表示 ====================
function showRules() {
  go('rules');
}

// ==================== ゲーム開始 ====================
function startGame(count) {
  // 動物をシャッフルして割り当て
  const shuffled = [...ANIMALS].sort(() => Math.random() - 0.5);

  state = {
    count,
    current: 0,
    animals: shuffled.slice(0, count),
    scores: Array(count).fill(0),
  };

  showTurnScreen();
}

// ==================== プレイヤー名 ====================
function pname(i) {
  return `プレイヤー ${i + 1}`;
}

// ==================== プログレスドット更新 ====================
function updateProgress() {
  const el = document.getElementById('progress');
  el.innerHTML = '';
  for (let i = 0; i < state.count; i++) {
    const d = document.createElement('div');
    d.className = [
      'pdot',
      i < state.current  ? 'done' : '',
      i === state.current ? 'current' : '',
    ].join(' ').trim();
    el.appendChild(d);
  }
}

// ==================== ターン準備画面 ====================
function showTurnScreen() {
  updateProgress();
  document.getElementById('turn-name').textContent = pname(state.current);
  go('turn');
}

// ==================== カウントダウン ====================
function startCountdown() {
  go('countdown');

  let n = 5;
  setCountdownNum(n);
  vibrate(60);

  if (countdownTimer) clearInterval(countdownTimer);

  countdownTimer = setInterval(() => {
    n--;
    if (n <= 0) {
      clearInterval(countdownTimer);
      showAnimal();
    } else {
      setCountdownNum(n);
      vibrate(60);
    }
  }, 1000);
}

function setCountdownNum(n) {
  const el = document.getElementById('countdown-num');
  el.textContent = n;
  // アニメーションをリセットして再生
  el.style.animation = 'none';
  void el.offsetWidth; // reflow
  el.style.animation = 'countIn 0.45s cubic-bezier(0.34, 1.56, 0.64, 1) both';
}

// ==================== 動物表示 ====================
function showAnimal() {
  const a = state.animals[state.current];

  document.getElementById('animal-who').textContent = pname(state.current);

  const emojiEl = document.getElementById('animal-show');
  emojiEl.textContent = a.e;
  // アニメーションリセット
  emojiEl.style.animation = 'none';
  void emojiEl.offsetWidth;
  emojiEl.style.animation =
    'animalPop 0.6s cubic-bezier(0.34, 1.56, 0.64, 1) both, animalWiggle 3s ease-in-out 0.6s infinite';

  vibrate([80, 40, 80]);
  go('animal');
}

// ==================== こたえあわせ画面へ ====================
function showGuessScreen() {
  document.getElementById('guess-name').textContent = pname(state.current);
  go('guess');
}

// ==================== 結果処理 ====================
function showResult(correct) {
  const a = state.animals[state.current];

  // 結果アイコン
  const iconEl = document.getElementById('r-icon');
  iconEl.textContent = correct ? '⭕' : '❌';
  iconEl.style.animation = 'none';
  void iconEl.offsetWidth;
  iconEl.style.animation = 'resultSpin 0.5s cubic-bezier(0.34, 1.56, 0.64, 1) both';

  // テキスト・動物
  document.getElementById('r-text').textContent = correct ? 'せいかい！！🎉' : 'ざんねん…！';
  document.getElementById('r-animal').textContent = a.e;
  document.getElementById('r-animal-name').textContent = `こたえ：${a.n}`;

  // 正解数を記録
  if (correct) state.scores[state.current]++;

  // 背景色だけ変更（background-image のグリッドを維持）
  document.getElementById('app').style.backgroundColor = correct
    ? '#00CF6E'   // 正解: グリーン
    : '#FF7043';  // 不正解: オレンジ

  // 次ボタンのテキスト
  const isLast = state.current >= state.count - 1;
  document.getElementById('r-next').textContent = isLast
    ? '✨ けっかはっぴょう！'
    : `つぎ：${pname(state.current + 1)} →`;

  // 画面切り替え（go()は使わず手動でactive切替 → 背景はすでに設定済み）
  document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
  document.getElementById('s-result').classList.add('active');

  vibrate(correct ? [100, 60, 100, 60, 200] : [300]);
}

// ==================== 次のプレイヤー ====================
function nextPlayer() {
  if (state.current >= state.count - 1) {
    showGameOver();
  } else {
    state.current++;
    showTurnScreen();
  }
}

// ==================== ゲームオーバー ====================
function showGameOver() {
  const list = document.getElementById('final-list');
  list.innerHTML = '';

  for (let i = 0; i < state.count; i++) {
    const a = state.animals[i];
    const ok = state.scores[i] > 0;

    const row = document.createElement('div');
    row.className = 'score-row';
    row.innerHTML = `
      <div class="score-emoji">${a.e}</div>
      <div class="score-pname">${pname(i)}</div>
      <div class="score-aname">${a.n}</div>
      <div class="score-result">${ok ? '⭕' : '❌'}</div>
    `;
    list.appendChild(row);
  }

  go('over');
}

// ==================== もう一回 ====================
function restartGame() {
  startGame(state.count);
}

// ==================== バイブレーション (Android対応) ====================
function vibrate(pattern) {
  if (navigator.vibrate) {
    navigator.vibrate(pattern);
  }
}

// ==================== 起動 ====================
document.addEventListener('DOMContentLoaded', () => {
  initBgAnimals();
});
