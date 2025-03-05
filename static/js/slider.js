document.addEventListener('DOMContentLoaded', function() {
    // 현재 날짜 표시
    const dateElement = document.getElementById('current-date');
    const currentDate = new Date();
    const formattedDate = currentDate.toLocaleDateString('ko-KR', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
    dateElement.textContent = `현재 날짜: ${formattedDate}`;
    
    // 드롭다운 메뉴 동작
    const dropdowns = document.querySelectorAll('.dropdown');
    
    dropdowns.forEach(dropdown => {
        dropdown.addEventListener('mouseover', function() {
            const content = this.querySelector('.dropdown-content');
            content.style.display = 'block';
            setTimeout(() => {
                content.style.opacity = '1';
                content.style.transform = 'translateY(0)';
            }, 10); // 약간의 딜레이로 부드러운 효과
        });
        
        dropdown.addEventListener('mouseout', function() {
            const content = this.querySelector('.dropdown-content');
            content.style.opacity = '0';
            content.style.transform = 'translateY(-10px)';
            setTimeout(() => {
                content.style.display = 'none';
            }, 300); // 전환 효과 시간과 맞춤
        });
    });
    
    // Swiper 슬라이더 초기화
    const swiper = new Swiper('.swiper-container', {
        // 기본 설정
        slidesPerView: 1, // 한 번에 보여줄 슬라이드 수
        spaceBetween: 0, // 슬라이드 간 간격
        loop: true, // 무한 루프
        autoplay: {
            delay: 5000, // 5초 간격으로 자동 슬라이드
            disableOnInteraction: false, // 사용자 상호작용 후에도 자동 재생 계속
        },
        
        // 페이지네이션 설정
        pagination: {
            el: '.swiper-pagination',
            clickable: true, // 페이지네이션 클릭 가능
        },
        
        // 네비게이션 버튼 설정
        navigation: {
            nextEl: '.swiper-button-next',
            prevEl: '.swiper-button-prev',
        },
        
        // 효과 설정
        effect: 'fade', // 페이드 효과 (옵션: 'slide', 'fade', 'cube', 'coverflow', 'flip')
        fadeEffect: {
            crossFade: true // 크로스 페이드 활성화
        },
        
        // 반응형 설정
        breakpoints: {
            // 768px 이하일 때
            768: {
                slidesPerView: 1,
                spaceBetween: 0
            }
        }
    });
});

document.getElementById("dark-mode-toggle").addEventListener("click", function () {
    document.body.classList.toggle("dark-mode");

    if (document.body.classList.contains("dark-mode")) {
        localStorage.setItem("darkMode", "enabled");
    } else {
        localStorage.setItem("darkMode", "disabled");
    }
});

// 페이지 로드 시 다크모드 설정 유지
if (localStorage.getItem("darkMode") === "enabled") {
    document.body.classList.add("dark-mode");
}
