document.addEventListener('DOMContentLoaded', function() {
    // Swiper 슬라이더 초기화
    const swiper = new Swiper('.swiper-container', {
        // 기본 설정
        slidesPerView: 1,
        spaceBetween: 0,
        loop: true,
        speed: 800, // 슬라이드 전환 속도 조정
        
        // 페이드 효과 제거하고 슬라이드 효과 사용
        effect: 'slide', // 'fade' 대신 'slide' 사용
        
        // 자동 재생 설정
        autoplay: {
            delay: 5000,
            disableOnInteraction: false,
        },
        
        // 네비게이션 버튼 설정
        navigation: {
            nextEl: '.swiper-button-next',
            prevEl: '.swiper-button-prev',
        },
        
        // 페이지네이션 설정
        pagination: {
            el: '.swiper-pagination',
            clickable: true,
        },
        
        // 오버플로우 처리
        watchOverflow: true,
        
        // 슬라이더가 화면 밖으로 나가지 않도록 설정
        observer: true,
        observeParents: true,
        
        // 슬라이드 효과를 더 부드럽게 만들기 위한 설정
        grabCursor: true,
        touchRatio: 1,
        touchAngle: 45,
        simulateTouch: true
    });
    
    // 다크 모드 토글 기능
    const darkModeToggle = document.getElementById("dark-mode-toggle");
    const modeText = document.getElementById("mode-text");
    
    if (darkModeToggle) {
        darkModeToggle.addEventListener("change", function() {
            document.body.classList.toggle("dark-mode");
            
            if (document.body.classList.contains("dark-mode")) {
                localStorage.setItem("darkMode", "enabled");
                if (modeText) modeText.textContent = "라이트모드";
            } else {
                localStorage.setItem("darkMode", "disabled");
                if (modeText) modeText.textContent = "다크모드";
            }
        });
        
        // 페이지 로드 시 다크모드 설정 유지
        if (localStorage.getItem("darkMode") === "enabled") {
            document.body.classList.add("dark-mode");
            darkModeToggle.checked = true;
            if (modeText) modeText.textContent = "라이트모드";
        }
    }
    
    // 플래시 메시지 관련 코드
    var flashMessages = document.querySelectorAll('.flash-message');
    flashMessages.forEach(function(message) {
        message.classList.add('show');
        setTimeout(function() {
            message.classList.remove('show');
        }, 3000);
    });
});

