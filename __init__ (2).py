<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
  <meta name="theme-color" content="#6366f1">
  <title>Английские слова</title>
  <script src="https://telegram.org/js/telegram-web-app.js"></script>
  <link rel="stylesheet" href="style.css">
</head>
<body>
  <main id="app"></main>
  <nav class="tabbar" id="tabbar">
    <a href="#train" data-tab="train"><span>🎯</span>Тренировка</a>
    <a href="#words" data-tab="words"><span>📖</span>Слова</a>
    <a href="#stats" data-tab="stats"><span>📊</span>Статистика</a>
    <a href="#points" data-tab="points"><span>⭐</span>Баллы</a>
    <a href="#settings" data-tab="settings"><span>⚙️</span>Ещё</a>
  </nav>
  <div id="toast" class="toast" hidden></div>
  <script src="app.js"></script>
</body>
</html>
