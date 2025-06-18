// 🔑 Находим кнопку и выпадающее меню по ID
const btn = document.getElementById('userMenuButton');
const dropdown = document.getElementById('userDropdown');

// ✅ Проверка: если оба элемента найдены, навешиваем обработчики
if (btn && dropdown) {
  // Когда кликаешь по кнопке (имя пользователя) — переключаем видимость меню
  btn.addEventListener('click', (e) => {
    e.stopPropagation(); // Чтобы клик не дошёл до window и не закрыл меню сразу
    dropdown.classList.toggle('hidden'); // Добавляем или убираем класс скрытия
  });

  // Если кликаешь в любое другое место на странице — меню закрывается
  window.addEventListener('click', () => {
    if (!dropdown.classList.contains('hidden')) {
      dropdown.classList.add('hidden');
    }
  });
}
