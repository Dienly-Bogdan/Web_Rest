const btn = document.getElementById('userMenuButton');
const dropdown = document.getElementById('userDropdown');

if (btn && dropdown) {
  btn.addEventListener('click', (e) => {
    e.stopPropagation();
    dropdown.classList.toggle('hidden');
  });

  window.addEventListener('click', () => {
    if (!dropdown.classList.contains('hidden')) {
      dropdown.classList.add('hidden');
    }
  });
}
