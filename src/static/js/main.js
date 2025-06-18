// При загрузке страницы выполняется loadMenuItems
// Это вытягивает меню из API и рендерит на страницу
document.addEventListener('DOMContentLoaded', () => {
    loadMenuItems();
});

// Функция загрузки пунктов меню
// Делает GET-запрос к /api/menu
// Парсит JSON и рендерит карточки блюд
function loadMenuItems() {
    fetch('/api/menu')
        .then(res => res.json())
        .then(data => {
            const grid = document.querySelector('.menu-grid');
            grid.innerHTML = ''; // очищаем контейнер перед рендером

            data.forEach(item => {
                // Создаём карточку для каждого блюда
                const card = document.createElement('div');
                card.className = 'menu-item';

                // Наполняем карточку HTML
                card.innerHTML = `
                    <img src="${item.image_url}" alt="${item.name}">
                    <div class="info">
                        <h3>${item.name}</h3>
                        <p>${item.description}</p>
                        <div class="price">${item.price} ₽</div>
                        <button onclick="addToCart(${item.id})">Добавить в корзину</button>
                    </div>
                `;

                // Добавляем карточку в контейнер
                grid.appendChild(card);
            });
        });
}

// Функция добавления товара в корзину
// Делает POST-запрос к /api/cart/add с id блюда
// После успешного запроса показывает alert
function addToCart(id) {
    fetch('/api/cart/add', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ item_id: id })
    }).then(() => {
        alert('Товар добавлен в корзину!');
    });
}