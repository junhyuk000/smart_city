document.addEventListener('DOMContentLoaded', function() {
    // 로컬 스토리지에서 즐겨찾기 가져오기
    const favorites = JSON.parse(localStorage.getItem('adminFavorites')) || [];
    
    // 즐겨찾기 별 초기화
    const stars = document.querySelectorAll('.favorite-star');
    stars.forEach(star => {
        const title = star.getAttribute('data-title');
        const url = star.getAttribute('data-url');
        
        // 이미 즐겨찾기된 항목은 활성화
        if (favorites.some(fav => fav.title === title)) {
            star.classList.add('active');
        }
        
        // 클릭 이벤트 추가
        star.addEventListener('click', function(e) {
            e.preventDefault();
            toggleFavorite(title, url, star);
        });
    });
    
    // 즐겨찾기 네비게이션 업데이트
    updateFavoritesNav();
});

// 즐겨찾기 토글 함수
function toggleFavorite(title, url, starElement) {
    const favorites = JSON.parse(localStorage.getItem('adminFavorites')) || [];
    const index = favorites.findIndex(fav => fav.title === title);
    
    if (index === -1) {
        // 즐겨찾기 추가
        favorites.push({ title, url });
        starElement.classList.add('active');
    } else {
        // 즐겨찾기 제거
        favorites.splice(index, 1);
        starElement.classList.remove('active');
    }
    
    // 로컬 스토리지에 저장
    localStorage.setItem('adminFavorites', JSON.stringify(favorites));
    
    // 즐겨찾기 네비게이션 업데이트
    updateFavoritesNav();
}

// 즐겨찾기 네비게이션 업데이트
function updateFavoritesNav() {
    const favorites = JSON.parse(localStorage.getItem('adminFavorites')) || [];
    const favoritesNav = document.getElementById('favorites-nav');
    const noFavoritesMessage = document.getElementById('no-favorites-message');
    
    // 기존 즐겨찾기 링크 제거 (라벨은 유지)
    const links = favoritesNav.querySelectorAll('a.nav-link');
    links.forEach(link => link.remove());
    
    // 즐겨찾기 없음 메시지 처리
    if (favorites.length === 0) {
        noFavoritesMessage.style.display = 'inline';
    } else {
        noFavoritesMessage.style.display = 'none';
        
        // 즐겨찾기 라벨 다음에 링크 추가
        const label = favoritesNav.querySelector('.favorites-label');
        
        favorites.forEach(fav => {
            const link = document.createElement('a');
            link.href = fav.url;
            link.className = 'nav-link';
            link.textContent = fav.title;
            favoritesNav.appendChild(link);
        });
    }
}