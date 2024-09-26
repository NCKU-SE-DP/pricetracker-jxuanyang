function toggleMenu() {
    const nav = document.getElementById('nav');
    if (nav.style.display === 'flex') {
        nav.style.display = 'none'; // 隱藏菜單
    } else {
        nav.style.display = 'flex'; // 顯示菜單
    }
}
