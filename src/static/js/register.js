// Берём кнопки "Sign Up" и "Sign In" из DOM
const signUpButton = document.getElementById('signUp');
const signInButton = document.getElementById('signIn');
const container = document.getElementById('container');

// Если нажали "Sign Up" — добавляем класс, который включает правую панель (например, форму регистрации)
signUpButton.addEventListener('click', () => {
    container.classList.add("right-panel-active");
});

// Если нажали "Sign In" — убираем этот класс, возвращая форму входа
signInButton.addEventListener('click', () => {
    container.classList.remove("right-panel-active");
});