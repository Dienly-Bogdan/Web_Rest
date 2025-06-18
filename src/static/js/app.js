
// Для подтверждения удаления блюда в админке
function confirmDeleteDish() {
    return confirm('Точно удалить это блюдо?');
}

// Для автообновления списка заказов 
function autoRefreshOrders(intervalSeconds = 20) {
    setTimeout(function() {
        window.location.reload();
    }, intervalSeconds * 1000);
}

// Подсветка изменившихся заказов 