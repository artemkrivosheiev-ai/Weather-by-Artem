// Скрипт реагирует на кнопку смены языка только для красоты, реальная смена выполняется сервером.
// Если элемент не найден — скрипт тихо выйдет.
(function() {
    const langBtn = document.getElementById('changeLang');
    if(!langBtn) return;

    // Просто меняем текст кнопки после клика (сервер всё равно перезагрузит страницу)
    langBtn.addEventListener('click', () => {
        // Короткая визуальная фича: поменяем текст до перезагрузки
        const current = langBtn.textContent.trim();
        if(current.includes('RU')) langBtn.textContent = '🌐 EN';
        else langBtn.textContent = '🌐 RU';
    });

    // Доп: добавим небольшую защиту, если элементы с id отсутствуют
    const cityInput = document.getElementById('cityInput');
    const showBtn = document.getElementById('showBtn');
    if(cityInput && showBtn) {
        cityInput.addEventListener('keydown', (e) => {
            if(e.key === 'Enter') {
                showBtn.click();
            }
        });
    }
})();


