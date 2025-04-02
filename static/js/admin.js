document.addEventListener('DOMContentLoaded', function() {
    // 로컬 스토리지에서 즐겨찾기 가져오기
    const favorites = JSON.parse(localStorage.getItem('adminFavorites')) || [];
    
    // 즐겨찾기 별 초기화
    const stars = document.querySelectorAll('.favorite-star');
    stars.forEach(star => {
        const title = star.getAttribute('data-title');
        const url = star.getAttribute('data-url');
        
        // URL을 기준으로 즐겨찾기 확인 (제목 대신)
        if (favorites.some(fav => fav.url === url)) {
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
    
    // 기존 데이터 마이그레이션 (한 번만 실행)
    migrateOldFavorites();
});

// 즐겨찾기 토글 함수
function toggleFavorite(title, url, starElement) {
    const favorites = JSON.parse(localStorage.getItem('adminFavorites')) || [];
    // URL을 기준으로 즐겨찾기 확인
    const index = favorites.findIndex(fav => fav.url === url);
    
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
            
            // 현재 페이지의 제목 업데이트 (선택 사항)
            updateFavoriteTitle(fav);
            
            favoritesNav.appendChild(link);
        });
    }
}

// 기존 데이터를 새 형식으로 마이그레이션
function migrateOldFavorites() {
    // 마이그레이션 완료 플래그 확인
    if (localStorage.getItem('favoriteMigrationDone')) {
        return;
    }
    
    const favorites = JSON.parse(localStorage.getItem('adminFavorites')) || [];
    let updated = false;
    
    // 현재 페이지의 모든 즐겨찾기 가능 항목을 가져옴
    const stars = document.querySelectorAll('.favorite-star');
    const currentItems = Array.from(stars).map(star => ({
        title: star.getAttribute('data-title'),
        url: star.getAttribute('data-url')
    }));
    
    // 즐겨찾기의 제목 업데이트 (URL은 동일하게 유지)
    favorites.forEach(fav => {
        const matchingItem = currentItems.find(item => item.url === fav.url);
        if (matchingItem && matchingItem.title !== fav.title) {
            fav.title = matchingItem.title;
            updated = true;
        }
    });
    
    if (updated) {
        localStorage.setItem('adminFavorites', JSON.stringify(favorites));
        updateFavoritesNav();
    }
    
    // 마이그레이션 완료 표시
    localStorage.setItem('favoriteMigrationDone', 'true');
}

// 현재 페이지의 정보로 즐겨찾기 제목 업데이트 (선택 사항)
function updateFavoriteTitle(favorite) {
    const stars = document.querySelectorAll('.favorite-star');
    for (const star of stars) {
        const url = star.getAttribute('data-url');
        if (url === favorite.url) {
            const currentTitle = star.getAttribute('data-title');
            if (favorite.title !== currentTitle) {
                favorite.title = currentTitle;
                return true;
            }
            break;
        }
    }
    return false;
}